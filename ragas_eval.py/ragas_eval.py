import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_groq import ChatGroq
from rag.retriever import search_query
from dotenv import load_dotenv
import json

load_dotenv(override=True)

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0, model_kwargs={"tool_choice": "none"})

golden_dataset = [
    {"question": "What credit utilization percentage triggers a payment on visit requirement?", "ground_truth": "Credit utilization above 85 percent triggers a payment on visit requirement."},
    {"question": "What is the maximum discount a field rep can authorize without approval?", "ground_truth": "A field rep can authorize up to 5 percent discount without approval."},
    {"question": "How many days without an order is considered a churn risk?", "ground_truth": "If a customer has not ordered in 45 or more days it is considered a churn risk."},
    {"question": "Which products are best suited for minimarket customers?", "ground_truth": "PRD-004 Fruit Drink Sachet 30s, PRD-003 Instant Drink Mix 1kg, PRD-006 Full Cream Milk 1L, PRD-007 Condensed Milk 500g, PRD-012 Candy Assorted 200g, PRD-016 Tomato Sauce 340g are best for minimarkets."},
    {"question": "What is the shelf life of Full Cream Milk 1L PRD-006?", "ground_truth": "30 days. Refrigerate at all times."},
    {"question": "What is the key sales message for Fruit Drink Sachet 30s PRD-004?", "ground_truth": "Impulse buy. Place near counter. High repeat purchase."},
    {"question": "What should a field rep do to prepare before a customer visit?", "ground_truth": "Review last 3 orders, check outstanding balance, review next visit date, note seasonal period, and check distributor inventory for fast-moving SKUs."},
    {"question": "What is the recommended order quantity formula?", "ground_truth": "Suggest order equals AMS multiplied by days until next visit divided by 30. Add 20 percent buffer if Q4 or festive season is upcoming."},
    {"question": "What is the strike rate KPI target for field reps?", "ground_truth": "More than 80 percent of visits should result in an order."},
    {"question": "What is the upsell strategy for minimarket customers?", "ground_truth": "Core SKUs are PRD-002, PRD-007, PRD-009, PRD-015. Upsell to PRD-001 if volume warrants 2kg size. Cross-sell PRD-012 with PRD-009 for confectionery bundle."},
]

def score_faithfulness(question, chunks, answer):
    prompt = f"""You are evaluating a RAG system.
Question: {question}
Retrieved chunks: {chr(10).join(chunks)}
Answer: {answer}

Does the answer contain ONLY information from the retrieved chunks with no hallucination?
Respond with JSON only: {{"score": 0.0, "reason": "one sentence"}}
Score 0 to 1 where 1 means fully grounded in chunks."""
    response = llm.invoke(prompt)
    return json.loads(response.content.strip())

def score_answer_relevancy(question, answer):
    prompt = f"""You are evaluating a RAG system.
Question: {question}
Answer: {answer}

Is the answer directly relevant to the question asked?
Respond with JSON only: {{"score": 0.0, "reason": "one sentence"}}
Score 0 to 1 where 1 means fully relevant."""
    response = llm.invoke(prompt)
    return json.loads(response.content.strip())

def score_context_recall(question, chunks, ground_truth):
    prompt = f"""You are evaluating a RAG system.
Question: {question}
Retrieved chunks: {chr(10).join(chunks)}
Ground truth answer: {ground_truth}

Do the retrieved chunks contain enough information to answer the question correctly?
Respond with JSON only: {{"score": 0.0, "reason": "one sentence"}}
Score 0 to 1 where 1 means chunks fully support the ground truth."""
    response = llm.invoke(prompt)
    return json.loads(response.content.strip())

def run_evaluation():
    faithfulness_scores    = []
    answer_relevancy_scores = []
    context_recall_scores  = []

    for item in golden_dataset:
        question    = item["question"]
        ground_truth = item["ground_truth"]

        chunks  = search_query(question, n_results=4)
        answer  = "\n".join(chunks)

        f  = score_faithfulness(question, chunks, answer)
        ar = score_answer_relevancy(question, answer)
        cr = score_context_recall(question, chunks, ground_truth)

        faithfulness_scores.append(f["score"])
        answer_relevancy_scores.append(ar["score"])
        context_recall_scores.append(cr["score"])

        print(f"\nQ: {question}")
        print(f"  Faithfulness    : {f['score']} — {f['reason']}")
        print(f"  Answer Relevancy: {ar['score']} — {ar['reason']}")
        print(f"  Context Recall  : {cr['score']} — {cr['reason']}")

    print("\n=== FINAL SCORES ===")
    print(f"Faithfulness     : {round(sum(faithfulness_scores)/len(faithfulness_scores), 2)}")
    print(f"Answer Relevancy : {round(sum(answer_relevancy_scores)/len(answer_relevancy_scores), 2)}")
    print(f"Context Recall   : {round(sum(context_recall_scores)/len(context_recall_scores), 2)}")

if __name__ == "__main__":
    run_evaluation()
from agents.prediction_agent import run as predict_run
from agents.customer_agent import run as customer_run
from tools.customer_tools import get_days_since_last_order
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv(override=True)

def route(query:str)->str:
    prompt=f"""You are a query router for a sales intelligence system.
    Given the query below, respond with exactly one word:
    - "prediction" if the query is about order quantity, sales forecast, how much to order
    - "customer" if the query is about credit, customer info, product recommendations, order history, policy

    Query: {query}

    Respond with only one word: prediction or customer"""

    llm=ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0
    )

    response = llm.invoke(prompt)

    output= response.content.strip().lower()

    return output


def ask(cust_cd: str, query: str):
    decision= route(query)
    match decision:
        case "prediction":
            return predict_run(cust_cd= cust_cd)
        case "customer":
            return customer_run(cust_cd=cust_cd,query=query)
        case _:
            return "Sorry, I could not understand your query."

def pre_visit_brief(cust_cd):
    customer_summary= customer_run(cust_cd=cust_cd,query="Give a full summary of this customer — credit status, order history, and product recommendations")
    predictions = predict_run(cust_cd=cust_cd)

    prompt=f"""
    You are a sales intelligence assistant preparing a pre-visit brief for a field rep.

    Customer Summary:
    {customer_summary}

    Order Quantity Predictions:
    {predictions}

    Write a concise pre-visit brief covering:
    1. Customer credit status and any risk flags
    2. Top recommended order quantities with confidence
    3. Key talking points for the rep
    Keep it under 200 words.
    """
    llm= ChatGroq(
            model="openai/gpt-oss-20b",
            temperature=0
        )
    
    response = llm.invoke(prompt)

    return response.content

def churn_risk_check(cust_cd: str) -> str:
    days= get_days_since_last_order(cust_cd=cust_cd)
    if days <= 40:
        return f"Customer is active. Last order {days} days ago. No churn risk."
    else:
        prompt=f"""
        A customer has not placed an order in {days} days.
        This is a churn risk. Generate a short recovery action plan for the field rep:
        - Suggested visit reason
        - Talking points to re-engage
        - Any incentive to offer
        Keep it under 100 words.
        """
        llm = ChatGroq(
            model="openai/gpt-oss-20b",
            temperature=0,
            model_kwargs={"tool_choice": "none"}
        )
            
        response = llm.invoke(prompt)
        
        return response.content


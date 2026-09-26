from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from langchain_groq import ChatGroq
from tools.prediction_tools import get_sales_data
import os
import json
from dotenv import load_dotenv

load_dotenv(override=True)


class PredictionState(TypedDict):
    cust_cd:    str
    prd_cd:     Optional[str]
    sales_data: list
    prediction: dict

def fetch_data(state):
    cust_cd= state['cust_cd']
    prd_cd=state['prd_cd']

    data= get_sales_data(cust_cd=cust_cd,prd_cd=prd_cd)
    return {**state,"sales_data":data}

def predict(state):
    sales_data= state['sales_data']
    cust_cd= state['cust_cd']

    if not sales_data:
        return {**state,"prediction":"Error! No Sales Data"}

    content=""

    content += f"Customer Code : {cust_cd}\n\n"

    for item in sales_data:
        
        content += f"Product : {item['PRD_DESC']}\n"
        content += f"Unit Price : INR{item['UNIT_PRICE']}\n"
        content += f"Last 3 months average: {item['l3m_mean']}\n"
        content += f"Last 6 months average: {item['l6m_mean']}\n"
        content += f"Last 12 months average: {item['l12m_mean']}\n"
        content += f"Monthly History: "
        for h in item['history']:
            content += f"  {h['order_month']}: {h['monthly_qty']} units\n"

        content += "\n"   # blank line between products


    content += """
    Based on this sales history recommend order quantity for each product.
    For each product respond with:
    - suggested_qty
    - confidence_pct (0 to 100)
    - reason (one sentence)

    Respond ONLY in JSON format, no extra text:
    [
    {"prd_cd": "PRD-001", "suggested_qty": 16, "confidence_pct": 82, "reason": "..."},
    ...
    ]
    """

    #Step4 Calling Chatgroq

    llm= ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0
    )

    response = llm.invoke(content)
    raw = response.content

    # Step 5 — strip markdown if LLM wraps response in ```json ... ```
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    # Step 6 — parse JSON and return updated state
    parsed = json.loads(raw)
    return {**state, "prediction": parsed}

def build_graph():
    graph =  StateGraph(PredictionState)

    graph.add_node("fetch_data",fetch_data)
    graph.add_node("predict",predict )

    graph.set_entry_point("fetch_data")
    graph.add_edge("fetch_data", "predict")
    graph.add_edge("predict",END)

    return graph.compile()

def run(cust_cd: str, prd_cd: str = None) -> dict:
    app=build_graph()
    result=app.invoke(
        {
            "cust_cd":cust_cd,
            "prd_cd":prd_cd,
            "sales_data":[],
            "prediction":{}
        }
    )
    return result['prediction']






    


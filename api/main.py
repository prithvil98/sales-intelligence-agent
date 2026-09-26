from fastapi import FastAPI
from pydantic import BaseModel
from agents.orchestrator import ask, pre_visit_brief, churn_risk_check
from tools.customer_tools import get_customer_info
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(title="Sales Intelligence API")

class AskRequest(BaseModel):
    cust_cd: str
    query: str

class CustomerRequest(BaseModel):
    cust_cd: str


#Main endpoint with cust_cd and query to get the answer
@app.post("/ask")
def ask_question(request: AskRequest):
    result = ask(cust_cd=request.cust_cd, query=request.query)
    return {"answer": result}

@app.post("/pre-visit-brief")
def visit_brief(request: CustomerRequest):
    result = pre_visit_brief(cust_cd=request.cust_cd)
    return {"brief": result}

@app.post("/churn-risk")
def churn_risk(request: CustomerRequest):
    result = churn_risk_check(cust_cd=request.cust_cd)
    return {"churn_risk": result}

@app.get("/customer/{cust_cd}")
def customer_info(cust_cd: str):
    result = get_customer_info(cust_cd=cust_cd)
    return result
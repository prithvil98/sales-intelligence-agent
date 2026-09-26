"""
This agent handles natural language questions about a customer — 
"What is CT50's credit status?", "What products should I recommend for this minimarket?
", "What did they order last 3 months?"

"""

from langgraph.graph import StateGraph, END
from typing import TypedDict
from langchain_groq import ChatGroq
from tools.customer_tools import get_customer_info, get_order_history
from rag.retriever import search_query
from dotenv import load_dotenv
import json

load_dotenv(override=True)

class CustomerState(TypedDict):
    cust_cd:       str
    query:         str
    customer_info: dict
    order_history: list
    rag_chunks:    list
    answer:        str

def fetch_customer_data(state):
    cust_cd=state['cust_cd']
    customer_info = get_customer_info(cust_cd=cust_cd)
    order_history= get_order_history(cust_cd=cust_cd,months=6)
    return {**state,"customer_info":customer_info,"order_history":order_history}

def rag_lookup(state):
    query=state['query']
    result= search_query(query,n_results=4)
    return {**state,"rag_chunks": result}

def synthesize(state):
    cust_cd=state['cust_cd']
    query=state['query']
    customer_info= state['customer_info']
    order_history=state['order_history']
    rag_chunks=state['rag_chunks']
    prompt="You are Sales Intelligence Assistant \n\n"
    prompt += f"Customer Code : {cust_cd}\n\n"
    prompt += f"Customer Info  : {json.dumps(customer_info)}\n\n"
    prompt += f"Order History : {json.dumps(order_history)}\n\n"
    prompt += f"Knowledge Base Context:\n{'\n'.join(rag_chunks)}\n\n"
    prompt += f"Question: {query}\n\n"

    prompt += f"Answer in 3-5 sentences. Be specific, use the data provided.\n\n"

    llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
    response = llm.invoke(prompt)
    return {**state, "answer": response.content}

def build_graph():
     graph= StateGraph(CustomerState)

     graph.add_node("fetch_customer_data",fetch_customer_data)
     graph.add_node("rag_lookup",rag_lookup)
     graph.add_node("synthesize", synthesize)

     graph.set_entry_point("fetch_customer_data")
     graph.add_edge("fetch_customer_data","rag_lookup")
     graph.add_edge("rag_lookup","synthesize")
     graph.add_edge("synthesize",END)

     return graph.compile()

def run(cust_cd: str, query: str) -> dict:
    app= build_graph()
    result = app.invoke(
        {
            "cust_cd":cust_cd,
            "query":query,
            "customer_info": {},
            "order_history": [],
            "rag_chunks":[],
            "answer":""
        }
    )
    return result['answer']

import gradio as gr
import requests

API_BASE = "http://127.0.0.1:8000"

def ask_agent(cust_cd, query):
    response = requests.post(f"{API_BASE}/ask", json={"cust_cd": cust_cd, "query": query})
    return response.json()["answer"]

def get_brief(cust_cd):
    response = requests.post(f"{API_BASE}/pre-visit-brief", json={"cust_cd": cust_cd})
    return response.json()["brief"]

def check_churn(cust_cd):
    response = requests.post(f"{API_BASE}/churn-risk", json={"cust_cd": cust_cd})
    return response.json()["churn_risk"]

with gr.Blocks(title="Sales Intelligence Agent") as demo:
    gr.Markdown("# Sales Intelligence Agent")

    with gr.Tab("Ask Agent"):
        cust_cd_input = gr.Textbox(label="Customer Code", placeholder="e.g. CT0000000050")
        query_input   = gr.Textbox(label="Your Question", placeholder="e.g. What is this customer's credit status?")
        ask_btn       = gr.Button("Ask")
        ask_output    = gr.Markdown(label="Answer")
        ask_btn.click(fn=ask_agent, inputs=[cust_cd_input, query_input], outputs=ask_output)

    with gr.Tab("Pre-Visit Brief"):
        brief_cust_cd = gr.Textbox(label="Customer Code", placeholder="e.g. CT0000000050")
        brief_btn     = gr.Button("Generate Brief")
        brief_output  = gr.Markdown(label="Brief")
        brief_btn.click(fn=get_brief, inputs=brief_cust_cd, outputs=brief_output)

    with gr.Tab("Churn Risk"):
        churn_cust_cd = gr.Textbox(label="Customer Code", placeholder="e.g. CT0000000050")
        churn_btn     = gr.Button("Check Risk")
        churn_output  = gr.Markdown(label="Result")
        churn_btn.click(fn=check_churn, inputs=churn_cust_cd, outputs=churn_output)

if __name__ == "__main__":
    demo.launch()
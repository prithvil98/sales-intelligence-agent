import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH= os.path.join(os.path.dirname(__file__), "..", "data", "sales_agent.db")

def _conn():
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    return conn

def get_sales_data(cust_cd,prd_cd= None):
    cutoff = (datetime.today() - timedelta(days=12 * 30)).strftime("%Y-%m-%d")

    # Build query and params dynamically
    where = "h.CUST_CD = ? AND h.VISIT_DT >= ?"
    params = [cust_cd, cutoff]

    if prd_cd:
        where += " AND h.PRD_CD = ?"
        params.append(prd_cd)

    query = """SELECT h.PRD_CD,p.PRD_DESC,p.UNIT_PRICE,
    strftime('%Y-%m', h.VISIT_DT) AS order_month,
    SUM(h.INV_QTY_SML) AS monthly_qty,
    SUM(h.INV_AMT)     AS monthly_amt
    FROM RPT_DAYSLSHISTDTL h
    JOIN MST_PRD p ON h.PRD_CD = p.PRD_CD WHERE """ + where + """    
    GROUP BY h.PRD_CD, order_month
    ORDER BY h.PRD_CD, order_month DESC
    """
    with _conn() as conn:
             row = conn.execute(query, params).fetchall()
    if not row:
        return []

    products = {}
    for r in row:
        d = dict(r)
        key = d["PRD_CD"]
        if key not in products:
            products[key] = {"PRD_CD": key, "PRD_DESC": d["PRD_DESC"], 
                            "UNIT_PRICE": d["UNIT_PRICE"], "history": []}
        products[key]["history"].append({
            "order_month": d["order_month"],
            "monthly_qty": d["monthly_qty"]
        })

    result = []
    for prd, data in products.items():
        qtys = [h["monthly_qty"] for h in data["history"]]
        data["l3m_mean"]  = round(sum(qtys[:3]) / len(qtys[:3]), 1) if qtys else 0
        data["l6m_mean"]  = round(sum(qtys[:6]) / len(qtys[:6]), 1) if len(qtys) >= 3 else 0
        data["l12m_mean"] = round(sum(qtys) / len(qtys), 1) if qtys else 0
        result.append(data)
    return result

    

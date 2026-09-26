import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH= os.path.join(os.path.dirname(__file__), "..", "data", "sales_agent.db")

def _conn():
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    return conn

def get_customer_info(cust_cd):
    query = "SELECT c.*, m.AMS from M_CUST c LEFT JOIN  M_MTHCUST m on c.CUST_CD= m.CUST_CD where c.CUST_CD=?"
    with _conn() as conn:
        row = conn.execute(query,(cust_cd,)).fetchone()
    if not row:
        return {"error": f"Customer {cust_cd} not found"}

    r= dict(row)
    r["credit_utilization_pct"]= round(((r["OUTSTANDING_BAL"]/r["CUST_CRDLMT"])*100),1)
    r["available_credit"]=round((r["CUST_CRDLMT"]- r["OUTSTANDING_BAL"]),2)
    return r


def get_order_history(cust_cd, months=6):
    cutoff = (datetime.today() - timedelta(days=months * 30)).strftime("%Y-%m-%d")
    query = """SELECT h.PRD_CD, p.PRD_DESC,
       strftime('%Y-%m', h.VISIT_DT) AS order_month,
       SUM(h.INV_QTY_SML) AS total_qty,
       SUM(h.INV_AMT) AS total_amt
    FROM RPT_DAYSLSHISTDTL h
    JOIN MST_PRD p ON h.PRD_CD = p.PRD_CD
    WHERE h.CUST_CD = ? AND h.VISIT_DT >= ?
    GROUP BY h.PRD_CD, order_month
    ORDER BY order_month DESC, total_amt DESC"""

    with _conn() as conn:
         row = conn.execute(query, (cust_cd, cutoff)).fetchall()
    if not row:
        return []    

    return [dict(r) for r in row]

def get_days_since_last_order(cust_cd):
    query="""SELECT MAX(VISIT_DT) as LAST_DT 
    FROM RPT_DAYSLSHISTDTL
    WHERE CUST_CD=?
    """

    with _conn() as conn:
        row = conn.execute(query, (cust_cd,)).fetchone()

    if not row:
        return 9999

    r= dict(row)

    if (r['LAST_DT'])== None:
        return 9999
    else:
        last_date= datetime.strptime(r["LAST_DT"], "%Y-%m-%d")
        no_of_days= (datetime.today()- last_date).days
        return int(no_of_days)


    

    

                                



    



        



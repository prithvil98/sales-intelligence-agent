# GenAI Sales Intelligence POC — Project Plan

> Built by: Prithvil K P  
> Purpose: Resume POC + Leadership pitch  
> Stack: Python, LangGraph, ChromaDB, Ollama / GPT-4o-mini, FastAPI, Streamlit, RAGAS

---

## Context — What already exists (don't duplicate)

| Repo | What it does | Tech |
|---|---|---|
| `nisa-svc` | API gateway — routes mobile app to SQL SPs or external NISA AI | Node.js |
| `np-agentic-ai` | Multi-agent system (Orchestrator, Prediction, Promotion, Customer-Sales) | YAML + Python (OpenAI Agents SDK) |
| `np-agentic-ai-eval` | LLM benchmark + RAG evaluation tool | Node.js |

**NISA has no RAG. Prediction uses a hardcoded formula. No explainability. No confidence scoring.**

---

## Architecture

```
User (plain English / voice / image)
        ↓
Orchestrator Agent  (LangGraph, Python)
        ├── customer query   → Customer Intelligence Agent
        └── order prediction → Prediction Agent

Special features (not in NISA):
    - pre_visit_brief()     ← orchestrator synthesises both agents into 1 brief
    - churn_risk_check()    ← proactive flag, no user prompt needed
```

### Customer Intelligence Agent
| Tool | What it does |
|---|---|
| `rag_search` | Searches knowledge docs via ChromaDB (product catalog, credit policy, sales guidelines) |
| `get_customer_info` | Gets credit limit, outstanding balance, customer type from SQLite |
| `get_order_history` | Gets last 3/6/12 month order data per customer-product |

### Prediction Agent
| Tool | What it does |
|---|---|
| `get_sales_data` | Pulls structured order history from SQLite |
| `predict_soq` | LLM reasons over data → suggested qty + confidence % + explanation |
| `whatif_simulate` | LLM simulates "what if discount = X%" scenarios |

---

## Special Features (differentiate from NISA)

| Feature | NISA | This POC |
|---|---|---|
| **Pre-visit brief** | ❌ Reactive only | ✅ Proactive one-page brief before visit |
| **Confidence scoring** | ❌ Returns number only | ✅ % confidence + reason on every recommendation |
| **What-if simulation** | ❌ Not possible | ✅ Simulate discount / promo impact |
| **Churn risk detection** | ❌ Never proactive | ✅ Flags customers not ordered in 40+ days |
| **RAG on knowledge** | ❌ No RAG at all | ✅ ChromaDB vector store on knowledge docs |

---

## Tech Stack

| Layer | Tool | Cost |
|---|---|---|
| Agent framework | LangGraph (Python) | Free |
| LLM (dev/test) | Ollama + Llama 3.1:8b | Free |
| LLM (demo) | GPT-4o-mini | ~$0.15 per 100 runs |
| Vector store | ChromaDB | Free |
| Database | SQLite | Free |
| Evaluation | RAGAS | Free |
| Tracing | LangSmith | Free (5000 traces/month) |
| API | FastAPI | Free |
| UI | Streamlit | Free |

---

## Project Folder Structure

```
Sales Agent/
├── PROJECT_PLAN.md           ← this file
├── README.md
├── requirements.txt
├── .env.example
│
├── data/
│   ├── generate_synthetic.py     ← creates SQLite DB with fake but realistic data
│   └── knowledge_docs/           ← RAG source documents
│       ├── product_catalog.txt
│       ├── credit_policy.txt
│       └── sales_guidelines.txt
│
├── rag/
│   ├── ingest.py                 ← chunk + embed docs → ChromaDB
│   └── retriever.py              ← query vector store
│
├── tools/
│   ├── customer_tools.py         ← get_customer_info, get_order_history
│   ├── inventory_tools.py        ← check_inventory
│   ├── prediction_tools.py       ← predict_soq, whatif_simulate
│   └── rag_tool.py               ← rag_search wrapper
│
├── agents/
│   ├── customer_agent.py         ← Customer Intelligence Agent (LangGraph node)
│   ├── prediction_agent.py       ← Prediction Agent (LangGraph node)
│   └── orchestrator.py           ← Orchestrator + pre_visit_brief + churn_risk
│
├── api/
│   └── main.py                   ← FastAPI endpoints
│
├── ui/
│   └── app.py                    ← Streamlit demo
│
└── eval/
    └── ragas_eval.py             ← RAGAS evaluation against golden dataset
```

---

## Database Schema (SQLite — same field names as SFA system)

### Master tables (insert first)
| Table | Key fields | Records |
|---|---|---|
| `M_DISTRIBUTOR` | DIST_CD (PK), DIST_NAME, COUNTRY_CD | 3 |
| `MST_PRDCAT` | PRDCAT2_CD (PK), PRDCAT_DESC | 4 |
| `MST_PRD` | PRD_CD (PK), PRD_DESC, PRDCAT2_CD (FK), UNIT_PRICE, UOM | 20 |
| `M_SALESMAN` | SALESMAN_CD (PK), DIST_CD (FK), SALESMAN_NAME, SALESMAN_TYPE | 10 |
| `M_CUST` | CUST_CD (PK), DIST_CD (FK), CUST_NAME, CUST_TYPE, CUST_HIER3, OUTSTANDING_BAL, CUST_CRDLMT, ADDR_1–5, ADDR_POSTAL, LATITUDE, LONGITUDE | 100 |
| `M_INVENTORY` | DIST_CD+PRD_CD (PK), QTY_ON_HAND, UOM | 60 |

### Transaction tables (insert after master)
| Table | Key fields | Records |
|---|---|---|
| `RPT_DAYSLSHISTDTL` | DIST_CD, CUST_CD (FK), PRD_CD (FK), PRDCAT2_CD (FK), VISIT_DT, INV_QTY_SML, INV_AMT, INV_DISC_AMT, INV_FOC_AMT | ~12,000 (12 months) |
| `MST_ROUTECUST` | DIST_CD, SALESMAN_CD (FK), CYCLE_CD, CUST_CD (FK), START_DT, END_DT | 100 |
| `M_ROUTEPLAN` | DIST_CD, SALESMAN_CD (FK), CUST_CD (FK), VISIT_DT | ~400 |
| `M_PRFMHDR_CUST` | DIST_CD, CUST_CD (FK), CAL_YEAR, CAL_MTH, SALES_AMT | ~1200 |
| `M_MTHCUST` | CUST_CD (FK), AMS | 100 |

### FK-safe insert order
```
1. M_DISTRIBUTOR → 2. MST_PRDCAT → 3. MST_PRD → 4. M_SALESMAN → 5. M_CUST
→ 6. M_INVENTORY → 7. MST_ROUTECUST → 8. M_ROUTEPLAN → 9. RPT_DAYSLSHISTDTL
→ 10. M_PRFMHDR_CUST → 11. M_MTHCUST
```

### Critical data generation rule
**Do NOT use `random.uniform()` for order quantities.**
Use `base_qty * random.uniform(0.8, 1.2)` where `base_qty` is fixed per customer-product pair.
This creates realistic buying patterns the Prediction Agent can reason about.
Some customers should skip 1–2 months randomly — creates churn scenarios for the agent to detect.

---

## Build Order (checkboxes)

- [ ] Step 1 — `data/generate_synthetic.py` — create SQLite DB with all tables
- [ ] Step 2 — `data/knowledge_docs/` — write 3 knowledge text files for RAG
- [ ] Step 3 — `rag/ingest.py` + `rag/retriever.py` — ChromaDB setup
- [ ] Step 4 — `tools/` — 5 Python tool functions
- [ ] Step 5 — `agents/prediction_agent.py` — LangGraph node
- [ ] Step 6 — `agents/customer_agent.py` — LangGraph node
- [ ] Step 7 — `agents/orchestrator.py` — wire + pre_visit_brief + churn_risk
- [ ] Step 8 — `ui/app.py` — Streamlit demo UI
- [ ] Step 9 — `eval/ragas_eval.py` — RAGAS evaluation

---

## Resume Bullet Points (draft)

- Built a multi-agent sales intelligence system using LangGraph and Python, with RAG on domain knowledge docs via ChromaDB, enabling natural language queries over structured SFA data
- Implemented proactive churn detection and pre-visit brief generation using LLM reasoning over 12-month order history — capabilities absent from the existing production NISA system
- Added confidence scoring and what-if scenario simulation to every SOQ recommendation, improving explainability for field sales representatives
- Evaluated RAG pipeline quality using RAGAS framework (faithfulness, answer relevancy, context recall metrics)

---

## Leadership Pitch (one paragraph)

> "The existing NISA system is middleware for an external Accenture AI product — Nestle has no ownership of that AI layer, and it has zero RAG capability. I built a self-contained sales intelligence agent in Python using open-source tools. A sales rep asks one question in plain English; the agent retrieves relevant product and policy knowledge, analyses customer order history, and produces a complete explained recommendation with confidence scoring. It also proactively generates pre-visit briefs and flags churn risks — neither of which NISA can do. The entire stack is portable, fully owned, and costs under $1 per month to run."

---
title: Multi Agent Customer Support
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: "4.44.0"
python_version: "3.10"
app_file: app.py
pinned: false
---

# 🤖 Multi-Agent Customer Support System
rest of your README content here...



# Multi-Agent Customer Support System

A LangGraph-powered customer support pipeline with RAG (ChromaDB + FAQ), LLM fallback, and human escalation.

## Tech Stack
- **LangGraph** — Agent orchestration
- **Groq (LLaMA 3.3 70B)** — LLM
- **ChromaDB** — Vector DB for RAG
- **Tavily** — Web search
- **Gradio** — UI
- **SQLite** — Ticket storage

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API keys
```bash
copy .env.example .env
```
Open `.env` and fill in:

### 5. Run
```bash
python main.py
```
Open http://localhost:7860

## Get API Keys
- **Groq** (free) → https://console.groq.com/keys
- **Tavily** (free) → https://app.tavily.com/home

Customer_Agent/
├── main.py
├── ui.py
├── graph.py
├── agents.py
├── triage_agent.py
├── router.py
├── chroma_store.py
├── faq.py
├── llm.py
├── search_tool.py
├── ticket_db.py
├── state.py
├── .env              ← never pushed (in .gitignore)
├── .env.example      ← safe to push
├── .gitignore
└── README.md         ← just created
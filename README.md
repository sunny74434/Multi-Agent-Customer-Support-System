🔗Deployment link: https://multi-agent-customer-support-system-n7nwbidbjn6m3r6vxjwphn.streamlit.app/

# 💬 Multi-Agent Customer Support System

A customer support assistant built with **LangGraph**, **Groq** and **Streamlit**. Each query is categorized, checked for sentiment, and routed through a set of cooperating agents. The system answers from an FAQ knowledge base, falls back to the LLM or a web search when needed, and escalates unhappy customers to a human. Every query creates exactly one support ticket.

## Features

- **Triage agent:** classifies each query as Technical, Billing, General or Web Search, and detects sentiment (positive, neutral, negative).
- **FAQ retrieval (RAG):** looks up relevant FAQs first and uses them as context for the answer.
- **Resolution agent:** a last-chance LLM answer when the FAQ lookup doesn't help.
- **Web search agent:** handles queries that need current information (Tavily).
- **Escalation agent:** negative-sentiment queries, or ones the system can't resolve, are escalated to a human.
- **Auto-reply generator:** polishes the final response.
- **Ticketing:** one ticket per query, viewable in the Tickets tab with status (open, escalated, resolved).
- **Streamlit UI:** three tabs: Support Agent, searchable FAQ, and Tickets.

## How it works

```
                    ┌──────────────┐
      Query ──────► │ Triage Agent │
                    └──────┬───────┘
          ┌────────────────┼─────────────────┐
          ▼                ▼                 ▼
   FAQ Retrieval     Web Search        Escalation
     (RAG)             Agent             Agent
     │     │              │                 │
resolved  failed          │                 │
     │     ▼              │                 │
     │  Resolution        │                 │
     │   Agent            │                 │
     │   │     │          │                 │
     │ resolved failed ───┼────────────────►│
     ▼   ▼                │                 │
 Auto-Reply Generator     │                 │
          │               │                 │
          └───────────────┴────────┬────────┘
                                   ▼
                              Save Ticket ──► END
```

## Tech stack

| Layer | Tool |
|---|---|
| UI | Streamlit |
| Agent orchestration | LangGraph |
| LLM | Groq (`openai/gpt-oss-120b`) via `langchain-groq` |
| Web search | Tavily |
| Storage | Ticket database (`ticket_db.py`) |

## Project structure

```
├── app.py             # Streamlit UI (Support Agent, FAQ, Tickets tabs)
├── graph.py           # LangGraph workflow: nodes and routing
├── llm.py             # Groq LLM setup
├── state.py           # Shared graph state
├── triage_agent.py    # Category and sentiment classification
├── agents.py          # FAQ retrieval, resolution, auto-reply, web search, escalation, save ticket
├── router.py          # Conditional routing between agents
├── faq.py             # FAQ knowledge base and search
├── ticket_db.py       # Ticket storage
└── requirements.txt
```

## Getting started

### 1. Clone and install

```bash
git clone <your-repo-url>
cd <your-repo-folder>
pip install -r requirements.txt
```

### 2. Set your API keys

Create a `.env` file in the project root:

```
GROQ_API_KEY=gsk_your_key_here
TAVILY_API_KEY=your_tavily_key_here
```

Get a Groq key at [console.groq.com](https://console.groq.com/keys) and a Tavily key at [tavily.com](https://tavily.com).

### 3. Run the app

```bash
streamlit run app.py
```

## Deploying on Streamlit Community Cloud

1. Push the project to GitHub.
2. Create a new app on [share.streamlit.io](https://share.streamlit.io) and point it at `app.py`.
3. Open **App settings → Secrets** and add:

   ```toml
   GROQ_API_KEY = "gsk_your_key_here"
   TAVILY_API_KEY = "your_tavily_key_here"
   ```

4. Reboot the app.

## Changing the model

The model is set in `llm.py`:

```python
llm = ChatGroq(
    temperature=0,
    groq_api_key=_api_key,
    model_name="openai/gpt-oss-120b",
)
```

Groq retires models from time to time (for example, `llama-3.3-70b-versatile` was shut down in August 2026). If you see a `model_not_found` error, check the current model list at [console.groq.com/docs/models](https://console.groq.com/docs/models) and the deprecations page at [console.groq.com/docs/deprecations](https://console.groq.com/docs/deprecations).

## Example queries

- "My internet connection keeps dropping every few hours."
- "I was charged twice for my subscription this month."
- "Where can I find my account settings?"
- "This is completely unacceptable! I've been waiting 2 weeks and nothing is resolved!" *(escalated)*

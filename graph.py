from langgraph.graph import StateGraph, END

from state import State
from triage_agent import triage_agent
from agents import (
    resolution_agent,
    auto_reply_generator,
    faq_kb_retrieval,
    web_search_agent,
    escalation_agent,
    save_ticket_agent,
)
from router import route_after_triage, route_after_faq, route_after_resolution

# ── Build the graph ────────────────────────────────────────────────
workflow = StateGraph(State)

# ── Nodes ──────────────────────────────────────────────────────────
workflow.add_node("triage_agent",         triage_agent)
workflow.add_node("faq_kb_retrieval",     faq_kb_retrieval)   # RAG: FAQ→LLM ctx→signal
workflow.add_node("resolution_agent",     resolution_agent)   # last-chance bare LLM
workflow.add_node("auto_reply_generator", auto_reply_generator)
workflow.add_node("web_search_agent",     web_search_agent)
workflow.add_node("escalation_agent",     escalation_agent)
workflow.add_node("save_ticket",          save_ticket_agent)  # ← only ONE ticket per query

# ── Entry ──────────────────────────────────────────────────────────
workflow.set_entry_point("triage_agent")

# ── Edge 1: Triage → RAG / Web / Escalate ─────────────────────────
workflow.add_conditional_edges(
    "triage_agent",
    route_after_triage,
    {
        "faq_kb_retrieval": "faq_kb_retrieval",  # normal queries → RAG first
        "web_search_agent": "web_search_agent",
        "escalation_agent": "escalation_agent",
    }
)

# ── Edge 2: RAG → polish or last-chance LLM ───────────────────────
workflow.add_conditional_edges(
    "faq_kb_retrieval",
    route_after_faq,
    {
        "auto_reply_generator": "auto_reply_generator",  # RAG resolved it
        "resolution_agent":     "resolution_agent",      # RAG failed → try bare LLM
    }
)

# ── Edge 3: Last-chance LLM → polish or escalate ──────────────────
workflow.add_conditional_edges(
    "resolution_agent",
    route_after_resolution,
    {
        "auto_reply_generator": "auto_reply_generator",  # LLM resolved it
        "escalation_agent":     "escalation_agent",      # everything failed → human
    }
)

# ── Edge 4: All terminal nodes → ONE save_ticket → END ────────────
# Ticket is created exactly once regardless of which path was taken.
workflow.add_edge("auto_reply_generator", "save_ticket")
workflow.add_edge("web_search_agent",     "save_ticket")
workflow.add_edge("escalation_agent",     "save_ticket")
workflow.add_edge("save_ticket",          END)

app = workflow.compile()

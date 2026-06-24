# router.py
from state import State


# ── Router 1: After Triage ─────────────────────────────────────────
def route_after_triage(state: State) -> str:
    """
    Web queries → web_search_agent.
    Negative sentiment → escalation_agent (fast-path, skip RAG).
    Everything else → faq_kb_retrieval FIRST (RAG is the primary resolver).
    """
    category  = state.get("category", "General").lower()
    sentiment = state.get("sentiment", "Neutral").lower()

    if sentiment == "negative":
        return "escalation_agent"
    elif category == "web":
        return "web_search_agent"
    else:
        # RAG (FAQ → LLM fallback) runs FIRST
        return "faq_kb_retrieval"


# ── Router 2: After RAG (FAQ / KB Retrieval) ──────────────────────
def route_after_faq(state: State) -> str:
    """
    If RAG resolved (Tier 1 FAQ hit or Tier 2 LLM-with-context hit):
        → auto_reply_generator (polish & ticket closed as 'resolved')

    If RAG could NOT resolve (Tier 3 — both FAQ and LLM failed):
        → resolution_agent (last-chance LLM with no FAQ context)
    """
    if state.get("resolved"):
        return "auto_reply_generator"
    else:
        return "resolution_agent"


# ── Router 3: After Resolution Agent (last-chance LLM) ────────────
def route_after_resolution(state: State) -> str:
    """
    If LLM resolved it → auto_reply_generator.
    If LLM also failed → escalation_agent (human handoff).
    """
    if state.get("resolved"):
        return "auto_reply_generator"
    else:
        return "escalation_agent"

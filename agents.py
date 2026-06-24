from langchain_core.prompts import ChatPromptTemplate

from state import State
from llm import llm
from search_tool import run_web_search
from chroma_store import rag_resolve
from ticket_db import save_ticket

# Re-export triage_agent from its own module so graph.py can import
# everything from one place if desired.
from triage_agent import triage_agent          # noqa: F401


# ── Helper: parse RESOLVED/UNRESOLVED from LLM output ─────────────
def parse_resolution(result: str) -> tuple[bool, str]:
    """
    Robustly parses LLM output regardless of formatting.
    Returns (resolved: bool, answer: str)
    """
    text = result.strip()
    low  = text.lower()

    if "unresolved:" in low:
        idx = low.index("unresolved:")
        return False, text[idx + 11:].strip()
    elif "resolved:" in low:
        idx = low.index("resolved:")
        return True, text[idx + 9:].strip()
    else:
        # LLM answered directly without prefix — treat as resolved
        return True, text


# ── Agent 2: Resolution Agent ──────────────────────────────────────
def resolution_agent(state: State) -> State:
    """
    First-pass LLM attempt to resolve the query.
    Sets resolved=True if it can answer confidently.
    If unresolved, the router will hand off to faq_kb_retrieval.
    """
    prompt = ChatPromptTemplate.from_template(
        "You are a customer support agent.\n\n"
        "Customer query: {query}\n"
        "Category: {category}\n\n"
        "Can you resolve this query with certainty right now?\n\n"
        "If YES — reply starting with exactly 'RESOLVED:' followed by your answer.\n"
        "If NO  — reply starting with exactly 'UNRESOLVED:' followed by why.\n\n"
        "Your response (must start with RESOLVED: or UNRESOLVED:):"
    )
    result = (prompt | llm).invoke({
        "query":    state["query"],
        "category": state["category"],
    }).content.strip()

    resolved, answer = parse_resolution(result)
    print(f"[Resolution Agent] resolved={resolved}  preview={answer[:60]}")
    return {"response": answer, "resolved": resolved}


# ── Agent 3: Auto Reply Generator ─────────────────────────────────
def auto_reply_generator(state: State) -> State:
    """
    Polishes the draft response into a professional customer-facing reply.
    Always the last content-generating node before save_ticket.
    """
    prompt = ChatPromptTemplate.from_template(
        "You are a professional customer support writer.\n"
        "Rewrite the following draft into a clear, friendly, professional reply.\n\n"
        "Customer query: {query}\n"
        "Draft response: {response}\n\n"
        "Final polished reply:"
    )
    response = (prompt | llm).invoke({
        "query":    state["query"],
        "response": state["response"],
    }).content.strip()

    print("[Auto Reply Generator] ✅ done")
    return {"response": response}


# ── Agent 4: FAQ / KB Retrieval  (RAG — three-tier pipeline) ──────
def faq_kb_retrieval(state: State) -> State:
    """
    Uses chroma_store.rag_resolve() which implements a three-tier flow:

        Tier 1 — FAQ semantic search (ChromaDB over faq.py data)
                 If high-confidence match → answer immediately.

        Tier 2 — LLM fallback with FAQ context as hints
                 If FAQ confidence is low → let LLM try with context.

        Tier 3 — Human escalation
                 If LLM also says UNRESOLVED → set resolved=False so
                 route_after_faq() hands off to escalation_agent.

    The router (router.py → route_after_faq) reads state["resolved"]
    to decide the next step.
    """
    result = rag_resolve(state["query"], llm)

    source = result["source"]
    print(f"[FAQ/KB RAG] source={source}  resolved={result['resolved']}")

    if result["resolved"]:
        return {
            "faq_context": result["faq_context"],
            "response":    result["answer"],
            "resolved":    True,
        }
    else:
        # Tier 3 path: signal escalation
        return {
            "faq_context": result["faq_context"],
            "response":    result["answer"],   # reason / partial context for human
            "resolved":    False,
        }


# ── Agent 5: Web Search Agent ──────────────────────────────────────
def web_search_agent(state: State) -> State:
    """
    Used when category is 'Web' — searches live internet data.
    """
    query       = state["query"]
    web_results = run_web_search(query)

    prompt = ChatPromptTemplate.from_template(
        "You are a helpful customer support agent.\n"
        "Customer asked: {query}\n\n"
        "Web search results:\n{web_results}\n\n"
        "Provide a clear helpful answer using these results. Cite sources where relevant."
    )
    response = (prompt | llm).invoke({
        "query":       query,
        "web_results": web_results,
    }).content.strip()

    print("[Web Search Agent] ✅ done")
    return {
        "web_results": web_results,
        "response":    response,
        "faq_context": None,
        "resolved":    True,
    }


# ── Agent 6: Escalation Agent ──────────────────────────────────────
def escalation_agent(state: State) -> State:
    """
    Triggered when ALL three tiers fail (FAQ → LLM → escalate) OR
    when sentiment is Negative (fast-path from triage).
    Prepares a human-readable handoff summary.
    """
    prompt = ChatPromptTemplate.from_template(
        "You are preparing a handoff summary for a human support agent.\n\n"
        "Customer query: {query}\n"
        "Category: {category}\n"
        "Sentiment: {sentiment}\n\n"
        "Write a brief internal summary so the human agent understands "
        "the context immediately:"
    )
    summary = (prompt | llm).invoke({
        "query":     state["query"],
        "category":  state["category"],
        "sentiment": state["sentiment"],
    }).content.strip()

    print("[Escalation Agent] ⚠️  escalating to human")
    return {
        "response": (
            "Your query has been escalated to a human support agent. "
            "They will reach out to you shortly.\n\n"
            f"[Agent Summary]: {summary}"
        ),
        "faq_context": None,
        "resolved":    False,
    }


# ── Agent 7: Save Ticket ───────────────────────────────────────────
def save_ticket_agent(state: State) -> State:
    """
    Final node — always runs last.
    Persists the ticket to SQLite with the correct resolved/escalated status.
    """
    status    = "resolved" if state.get("resolved") else "escalated"
    ticket_id = save_ticket(
        query     = state["query"],
        category  = state.get("category",  "General"),
        sentiment = state.get("sentiment", "Neutral"),
        response  = state.get("response",  ""),
        status    = status,
    )
    print(f"[Save Ticket] ID={ticket_id}  status={status}")
    return {"ticket_id": ticket_id}

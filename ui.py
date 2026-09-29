import html
import os

import streamlit as st

# Must be the first Streamlit call
st.set_page_config(page_title="Customer Support Agent", page_icon="💬", layout="wide")

# Make Streamlit secrets visible as env vars BEFORE importing llm / search_tool
try:
    for _key in ("GROQ_API_KEY", "TAVILY_API_KEY"):
        if _key in st.secrets:
            os.environ.setdefault(_key, st.secrets[_key])
except Exception:
    pass  # no secrets file (e.g. local run using .env)

from graph import app as support_graph          # noqa: E402
from faq import search_faqs                     # noqa: E402
from ticket_db import get_all_tickets           # noqa: E402

# ── Emoji maps ─────────────────────────────────────────────────────
SENTIMENT_EMOJI = {
    "positive": "😊 Positive",
    "neutral":  "😐 Neutral",
    "negative": "😟 Negative — Escalated",
}
CATEGORY_EMOJI = {
    "technical": "🔧 Technical",
    "billing":   "💳 Billing",
    "general":   "💬 General",
    "web":       "🌐 Web Search",
}
EXAMPLES = [
    "My internet connection keeps dropping every few hours.",
    "I was charged twice for my subscription this month.",
    "Where can I find my account settings?",
    "This is completely unacceptable! I've been waiting 2 weeks and nothing is resolved!",
]

# ── CSS (trimmed from the Gradio version; no Gradio-only selectors) ─
st.markdown(
    """
<style>
.app-header {
    background: linear-gradient(135deg, #1a1f2e 0%, #16213e 50%, #0f3460 100%);
    border-radius: 16px; padding: 32px 40px; margin-bottom: 16px;
    border: 1px solid #2a3550; text-align: center;
}
.app-header h1 { font-size: 2rem; font-weight: 700; color: #e2e8f0; margin: 0 0 8px 0; }
.app-header p  { color: #94a3b8; font-size: 0.95rem; margin: 0; }
.accent { color: #60a5fa; }
.faq-stats { display: flex; gap: 12px; justify-content: center; margin-top: 16px; flex-wrap: wrap; }
.faq-stat {
    background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.2);
    border-radius: 20px; padding: 4px 14px; font-size: 0.8rem; color: #93c5fd;
}
.section-label {
    font-size: 0.75rem; color: #64748b; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px;
}
.badge {
    background: #131720; border: 2px solid #2a3550; border-radius: 8px;
    color: #60a5fa; font-weight: 600; text-align: center; padding: 10px;
}
.faq-item {
    background: #1a1f2e; border: 1px solid #2a3550; border-radius: 12px;
    padding: 18px 20px; margin-bottom: 12px; transition: all 0.2s ease;
}
.faq-item:hover { border-color: #3b82f6; transform: translateY(-2px); }
.faq-category-tag {
    display: inline-block; font-size: 0.72rem; font-weight: 700; color: #60a5fa;
    background: rgba(59,130,246,0.12); border: 1px solid rgba(59,130,246,0.25);
    border-radius: 20px; padding: 2px 10px; margin-bottom: 10px; text-transform: uppercase;
}
.faq-question { font-size: 0.95rem; font-weight: 600; color: #e2e8f0; margin-bottom: 8px; }
.faq-answer   { font-size: 0.88rem; color: #94a3b8; line-height: 1.65; }
</style>
""",
    unsafe_allow_html=True,
)


# ── Core logic ─────────────────────────────────────────────────────
def run_customer_support(query: str) -> dict:
    results = support_graph.invoke({"query": query})
    return {
        "category":  results["category"],
        "sentiment": results["sentiment"],
        "response":  results["response"],
        "ticket_id": results.get("ticket_id", "N/A"),
    }


def render_tickets() -> str:
    tickets = get_all_tickets()
    if not tickets:
        return (
            "<p style='color:#64748b;text-align:center;padding:40px'>"
            "No tickets yet. Submit a query to create one.</p>"
        )
    colors = {"open": "#22c55e", "escalated": "#ef4444", "resolved": "#3b82f6"}
    rows = []
    for t in tickets:
        color = colors.get(t["status"], "#94a3b8")
        query = str(t["query"])
        short = html.escape(query[:120]) + ("..." if len(query) > 120 else "")
        rows.append(
            f"""<div class="faq-item">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
<b style="color:#60a5fa;font-size:0.95rem">🎫 #{html.escape(str(t['id']))}</b>
<span style="color:{color};font-size:0.78rem;font-weight:700;background:rgba(0,0,0,0.3);padding:2px 10px;border-radius:20px;border:1px solid {color}">● {html.escape(str(t['status']).upper())}</span>
</div>
<div style="color:#e2e8f0;margin-bottom:6px;font-size:0.92rem">{short}</div>
<div style="color:#64748b;font-size:0.78rem;display:flex;gap:12px">
<span>📁 {html.escape(str(t['category']))}</span>
<span>💬 {html.escape(str(t['sentiment']))}</span>
<span>🕐 {html.escape(str(t['timestamp']))}</span>
</div>
</div>"""
        )
    return "".join(rows)


# ── Session state ──────────────────────────────────────────────────
st.session_state.setdefault("query_text", "")
st.session_state.setdefault("result", None)


def set_example(text: str):
    st.session_state.query_text = text


def clear_all():
    st.session_state.query_text = ""
    st.session_state.result = None


# ── Header ─────────────────────────────────────────────────────────
st.markdown(
    """
<div class="app-header">
  <h1>Multi-Agent <span class="accent">Customer Support</span> System</h1>
  <p>Powered by LLaMA 3.3 70B &nbsp;·&nbsp; Categorizes, analyzes sentiment, and routes your query automatically</p>
  <div class="faq-stats">
    <span class="faq-stat">🔧 5 Technical FAQs</span>
    <span class="faq-stat">💳 5 Billing FAQs</span>
    <span class="faq-stat">💬 5 General FAQs</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

tab_agent, tab_faq, tab_tickets = st.tabs(["💬 Support Agent", "📚 FAQ", "🎫 Tickets"])

# ── Tab 1: Support Agent ───────────────────────────────────────────
with tab_agent:
    left, right = st.columns(2, gap="large")

    with left:
        st.markdown('<p class="section-label">Your Query</p>', unsafe_allow_html=True)
        with st.form("query_form", border=False):
            st.text_area(
                "Query",
                key="query_text",
                height=140,
                placeholder="Describe your issue or question here...",
                label_visibility="collapsed",
            )
            c1, c2 = st.columns([3, 1])
            submitted = c1.form_submit_button(
                "Submit Query →", type="primary", use_container_width=True
            )
            c2.form_submit_button("Clear", on_click=clear_all, use_container_width=True)

        st.markdown('<p class="section-label">Try an example</p>', unsafe_allow_html=True)
        for i, ex in enumerate(EXAMPLES):
            st.button(ex, key=f"ex_{i}", on_click=set_example, args=(ex,), use_container_width=True)

    if submitted:
        query = st.session_state.query_text.strip()
        if not query:
            st.session_state.result = {"error": "Please enter a query before submitting."}
        else:
            with st.spinner("Agents are working on your query..."):
                try:
                    st.session_state.result = run_customer_support(query)
                except Exception as e:
                    st.session_state.result = {"error": f"Something went wrong: {e}"}

    with right:
        result = st.session_state.result
        if result:
            if "error" in result:
                st.warning(result["error"])
            else:
                st.markdown('<p class="section-label">Analysis Results</p>', unsafe_allow_html=True)
                b1, b2 = st.columns(2)
                cat = CATEGORY_EMOJI.get(result["category"].lower(), result["category"])
                sen = SENTIMENT_EMOJI.get(result["sentiment"].lower(), result["sentiment"])
                b1.markdown(f'<div class="badge">{html.escape(cat)}</div>', unsafe_allow_html=True)
                b2.markdown(f'<div class="badge">{html.escape(sen)}</div>', unsafe_allow_html=True)

                st.markdown('<p class="section-label" style="margin-top:16px">Agent Response</p>',
                            unsafe_allow_html=True)
                with st.container(border=True):
                    st.write(result["response"])
                    st.caption(f"🎫 Ticket ID: #{result['ticket_id']}")

# ── Tab 2: FAQ ─────────────────────────────────────────────────────
with tab_faq:
    s1, s2 = st.columns([4, 1])
    term = s1.text_input(
        "Search",
        placeholder="🔍  Search FAQs — e.g. 'refund', 'password', 'cancel'...",
        label_visibility="collapsed",
    )
    s2.button("Search", use_container_width=True)  # a click simply reruns with the current text

    category = st.radio(
        "Category",
        ["All", "Technical", "Billing", "General"],
        horizontal=True,
        label_visibility="collapsed",
    )
    st.divider()
    st.html(search_faqs(term, category))

# ── Tab 3: Tickets ─────────────────────────────────────────────────
with tab_tickets:
    t1, t2 = st.columns([4, 1])
    t1.markdown('<p class="section-label">All Support Tickets</p>', unsafe_allow_html=True)
    t2.button("🔄 Refresh", use_container_width=True)  # rerun re-reads the DB
    st.divider()
    st.html(render_tickets())

    
from typing import Dict
import gradio as gr
from graph import app
from faq import search_faqs
from ticket_db import get_all_tickets, update_ticket_status

# ── Emoji Maps ─────────────────────────────────────────────────────
SENTIMENT_EMOJI = {
    "positive": "😊 Positive",
    "neutral":  "😐 Neutral",
    "negative": "😟 Negative — Escalated",
}
CATEGORY_EMOJI = {
    "technical": "🔧 Technical",
    "billing":   "💳 Billing",
    "general":   "💬 General",
    "web":       "🌐 Web Search",    # ADD THIS
}

# ── Core Logic ─────────────────────────────────────────────────────
def run_customer_support(query: str) -> Dict[str, str]:
    results = app.invoke({"query": query})
    return {
        "category":  results["category"],
        "sentiment": results["sentiment"],
        "response":  results["response"],
        "ticket_id": results.get("ticket_id", "N/A"),   # ADD
    }

def process_query(query: str):
    if not query.strip():
        return (
            gr.update(value=""),
            gr.update(value=""),
            gr.update(value="Please enter a query before submitting."),
            gr.update(visible=True),
            gr.update() 
        )
    result    = run_customer_support(query)
    category  = CATEGORY_EMOJI.get(result["category"].lower(),  result["category"])
    sentiment = SENTIMENT_EMOJI.get(result["sentiment"].lower(), result["sentiment"])
    ticket_id = result.get("ticket_id", "N/A")                          # ADD
    response  = result["response"] + f"\n\n🎫 Ticket ID: #{ticket_id}"  # ADD
    return (
        gr.update(value=category),
        gr.update(value=sentiment),
        gr.update(value=response),                                       # changed
        gr.update(visible=True),
        gr.update(value=render_tickets())
    )

def clear_all():
    return (
        gr.update(value=""),
        gr.update(value=""),
        gr.update(value=""),
        gr.update(value=""),
        gr.update(visible=False),
    )
    
def render_tickets():
    tickets = get_all_tickets()
    if not tickets:
        return "<p style='color:#64748b;text-align:center;padding:40px'>No tickets yet. Submit a query to create one.</p>"
    rows = ""
    for t in tickets:
        color = {
            "open":      "#22c55e",
            "escalated": "#ef4444",
            "resolved":  "#3b82f6"
        }.get(t["status"], "#94a3b8")
        rows += f"""
        <div class="faq-item">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                <b style="color:#60a5fa;font-size:0.95rem">🎫 #{t['id']}</b>
                <span style="color:{color};font-size:0.78rem;font-weight:700;
                      background:rgba(0,0,0,0.3);padding:2px 10px;border-radius:20px;
                      border:1px solid {color}">
                    ● {t['status'].upper()}
                </span>
            </div>
            <div style="color:#e2e8f0;margin-bottom:6px;font-size:0.92rem">
                {t['query'][:120]}{'...' if len(t['query']) > 120 else ''}
            </div>
            <div style="color:#64748b;font-size:0.78rem;display:flex;gap:12px">
                <span>📁 {t['category']}</span>
                <span>💬 {t['sentiment']}</span>
                <span>🕐 {t['timestamp']}</span>
            </div>
        </div>
        """
    return rows

# ── Custom CSS with Animations ─────────────────────────────────────
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideIn {
    from { opacity: 0; transform: translateX(-10px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-3px); }
}

body, .gradio-container {
    font-family: 'Inter', sans-serif !important;
    background: #0f1117 !important;
}

.app-header {
    background: linear-gradient(135deg, #1a1f2e 0%, #16213e 50%, #0f3460 100%);
    border-radius: 16px; padding: 36px 40px; margin-bottom: 8px;
    border: 1px solid #2a3550; text-align: center;
    animation: fadeInUp 0.6s ease-out;
}

.app-header h1 { 
    font-size: 2rem; font-weight: 700; color: #e2e8f0; 
    margin: 0 0 8px 0; letter-spacing: -0.5px; 
}

.app-header p  { 
    color: #94a3b8; font-size: 0.95rem; margin: 0; 
}

.accent { 
    color: #60a5fa; 
    animation: pulse 2s ease-in-out infinite; 
}

.tab-nav button {
    background: transparent !important; color: #64748b !important;
    border: none !important; border-bottom: 2px solid transparent !important;
    font-weight: 600 !important; font-size: 0.9rem !important;
    padding: 10px 20px !important; border-radius: 0 !important;
    transition: all 0.3s ease !important; cursor: pointer !important;
}

.tab-nav button:hover {
    color: #94a3b8 !important;
    transform: translateY(-2px) !important;
}

.tab-nav button.selected { 
    color: #60a5fa !important; 
    border-bottom-color: #60a5fa !important;
    animation: slideIn 0.3s ease-out;
}

label, .block > label {
    font-size: 0.78rem !important; font-weight: 600 !important; color: #64748b !important;
    text-transform: uppercase !important; letter-spacing: 0.08em !important; margin-bottom: 6px !important;
}

textarea, input[type="text"] {
    background: #131720 !important; border: 1px solid #2a3550 !important;
    border-radius: 10px !important; color: #e2e8f0 !important;
    font-size: 0.95rem !important; padding: 12px 16px !important;
    transition: all 0.3s ease !important;
}

textarea:focus, input[type="text"]:focus {
    border-color: #3b82f6 !important; outline: none !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
    background: #1a1f2e !important;
}

.btn-submit {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 50%, #1d4ed8 100%) !important;
    color: #fff !important; border: none !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: 0.95rem !important; padding: 12px 28px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
    cursor: pointer !important;
}

.btn-submit:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(59, 130, 246, 0.5) !important;
    background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 50%, #2563eb 100%) !important;
}

.btn-submit:active {
    transform: translateY(0px) !important;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4) !important;
}

.btn-clear {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 50%, #b91c1c 100%) !important;
    color: #fff !important; border: none !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: 0.95rem !important; padding: 12px 20px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3) !important;
    cursor: pointer !important;
}

.btn-clear:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(239, 68, 68, 0.5) !important;
    background: linear-gradient(135deg, #f87171 0%, #ef4444 50%, #dc2626 100%) !important;
}

.btn-clear:active {
    transform: translateY(0px) !important;
    box-shadow: 0 2px 8px rgba(239, 68, 68, 0.4) !important;
}

.btn-search {
    background: linear-gradient(135deg, #10b981 0%, #059669 50%, #047857 100%) !important;
    color: #fff !important; border: none !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: 0.9rem !important; padding: 8px 20px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
    cursor: pointer !important;
}

.btn-search:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5) !important;
    background: linear-gradient(135deg, #34d399 0%, #10b981 50%, #059669 100%) !important;
}

.btn-search:active {
    transform: translateY(0px) !important;
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.4) !important;
}

.result-badge textarea {
    background: #131720 !important; border: 2px solid #2a3550 !important;
    border-radius: 8px !important; color: #60a5fa !important;
    font-weight: 600 !important; text-align: center !important; padding: 10px !important;
    animation: fadeInUp 0.5s ease-out;
    transition: all 0.3s ease !important;
}

.result-badge textarea:hover {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
}

.response-box textarea {
    background: #131720 !important; border: 1px solid #2a3550 !important;
    border-radius: 10px !important; color: #cbd5e1 !important;
    font-size: 0.92rem !important; line-height: 1.6 !important;
    animation: fadeInUp 0.6s ease-out;
    transition: border-color 0.3s ease !important;
}

.response-box textarea:focus {
    border-color: #3b82f6 !important;
}

.results-section {
    background: #1a1f2e; border: 1px solid #2a3550;
    border-radius: 14px; padding: 24px; margin-top: 8px;
    animation: fadeInUp 0.5s ease-out;
}

.divider { 
    border: none; border-top: 1px solid #2a3550; margin: 20px 0; 
}

.section-label {
    font-size: 0.75rem; color: #64748b; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px;
}

.faq-item {
    background: #1a1f2e; border: 1px solid #2a3550;
    border-radius: 12px; padding: 18px 20px; margin-bottom: 12px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    cursor: pointer !important;
}

.faq-item:hover { 
    border-color: #3b82f6;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
    background: #1f2437;
}

.faq-category-tag {
    display: inline-block; font-size: 0.72rem; font-weight: 700; color: #60a5fa;
    background: rgba(59,130,246,0.12); border: 1px solid rgba(59,130,246,0.25);
    border-radius: 20px; padding: 2px 10px; margin-bottom: 10px;
    text-transform: uppercase; letter-spacing: 0.06em;
    transition: all 0.3s ease !important;
}

.faq-item:hover .faq-category-tag {
    background: rgba(59, 130, 246, 0.25);
    border-color: rgba(59, 130, 246, 0.5);
}

.faq-question { 
    font-size: 0.95rem; font-weight: 600; color: #e2e8f0; 
    margin-bottom: 8px;
    transition: color 0.3s ease !important;
}

.faq-item:hover .faq-question {
    color: #60a5fa;
}

.faq-answer   { 
    font-size: 0.88rem; color: #94a3b8; line-height: 1.65; 
}

.faq-cat-btn {
    background: #1e2433 !important; color: #94a3b8 !important;
    border: 1px solid #2a3550 !important; border-radius: 20px !important;
    font-size: 0.82rem !important; font-weight: 500 !important; padding: 6px 16px !important;
    transition: all 0.3s ease !important;
    cursor: pointer !important;
}

.faq-cat-btn:hover {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
    color: #fff !important;
    border-color: #4f46e5 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
}

.faq-results { 
    max-height: 520px; 
    overflow-y: auto; 
    padding-right: 4px; 
    animation: fadeInUp 0.5s ease-out;
}

.faq-stats { 
    display: flex; 
    gap: 12px; 
    justify-content: center; 
    margin-top: 16px; 
    flex-wrap: wrap; 
}

.faq-stat {
    background: rgba(59,130,246,0.1); 
    border: 1px solid rgba(59,130,246,0.2);
    border-radius: 20px; 
    padding: 4px 14px; 
    font-size: 0.8rem; 
    color: #93c5fd; 
    font-weight: 500;
    transition: all 0.3s ease !important;
    animation: fadeInUp 0.6s ease-out backwards;
}

.faq-stat:nth-child(1) { animation-delay: 0.1s; }
.faq-stat:nth-child(2) { animation-delay: 0.2s; }
.faq-stat:nth-child(3) { animation-delay: 0.3s; }

.faq-stat:hover {
    background: rgba(59, 130, 246, 0.25);
    border-color: rgba(59, 130, 246, 0.5);
    transform: scale(1.05);
}
"""

# ── Gradio UI ──────────────────────────────────────────────────────
with gr.Blocks(css=custom_css, title="Customer Support Agent") as gui:

    gr.HTML("""
    <div class="app-header">
        <h1>Multi-Agent <span class="accent">Customer Support</span> System</h1>
        <p>Powered by LLaMA 3.3 70B &nbsp;·&nbsp; Categorizes, analyzes sentiment, and routes your query automatically</p>
        <div class="faq-stats">
            <span class="faq-stat">🔧 5 Technical FAQs</span>
            <span class="faq-stat">💳 5 Billing FAQs</span>
            <span class="faq-stat">💬 5 General FAQs</span>
        </div>
    </div>
    """)

    with gr.Tabs(elem_classes=["tab-nav"]):

        # ── Tab 1: Support Agent ─────────────────────────────────────
        with gr.Tab("💬 Support Agent"):
            with gr.Row(equal_height=False):
                with gr.Column(scale=1):
                    gr.HTML('<p class="section-label">Your Query</p>')
                    query_input = gr.Textbox(
                        lines=5, placeholder="Describe your issue or question here...",
                        show_label=False, container=False,
                    )
                    with gr.Row():
                        submit_btn = gr.Button("Submit Query →", elem_classes=["btn-submit"], scale=3)
                        clear_btn  = gr.Button("Clear",          elem_classes=["btn-clear"],  scale=1)

                    gr.HTML('<hr class="divider">')
                    gr.HTML('<p class="section-label">Try an example</p>')
                    gr.Examples(
                        examples=[
                            ["My internet connection keeps dropping every few hours."],
                            ["I was charged twice for my subscription this month."],
                            ["Where can I find my account settings?"],
                            ["This is completely unacceptable! I've been waiting 2 weeks and nothing is resolved!"],
                        ],
                        inputs=query_input, label="",
                    )

                with gr.Column(scale=1):
                    results_block = gr.Column(visible=False, elem_classes=["results-section"])
                    with results_block:
                        gr.HTML('<p class="section-label">Analysis Results</p>')
                        with gr.Row():
                            category_out  = gr.Textbox(label="Category",  interactive=False, elem_classes=["result-badge"])
                            sentiment_out = gr.Textbox(label="Sentiment", interactive=False, elem_classes=["result-badge"])
                        gr.HTML('<hr class="divider">')
                        gr.HTML('<p class="section-label">Agent Response</p>')
                        response_out = gr.Textbox(
                            lines=10, interactive=False, show_label=False,
                            container=False, elem_classes=["response-box"],
                        )

        # ── Tab 2: FAQ ───────────────────────────────────────────────
        with gr.Tab("📚 FAQ"):
            with gr.Row():
                with gr.Column(scale=3):
                    faq_search = gr.Textbox(
                        placeholder="🔍  Search FAQs — e.g. 'refund', 'password', 'cancel'...",
                        show_label=False, container=False,
                    )
                with gr.Column(scale=1, min_width=120):
                    faq_search_btn = gr.Button("Search", elem_classes=["btn-search"])

            with gr.Row():
                faq_cat_all       = gr.Button("All",          elem_classes=["faq-cat-btn"])
                faq_cat_technical = gr.Button("🔧 Technical", elem_classes=["faq-cat-btn"])
                faq_cat_billing   = gr.Button("💳 Billing",   elem_classes=["faq-cat-btn"])
                faq_cat_general   = gr.Button("💬 General",   elem_classes=["faq-cat-btn"])

            gr.HTML('<hr class="divider">')
            faq_output = gr.HTML(value=search_faqs("", "All"), elem_classes=["faq-results"])
        
        # ── Tab 3: Tickets ───────────────────────────────────────────
        with gr.Tab("🎫 Tickets"):
            with gr.Row():
                with gr.Column(scale=3):
                    gr.HTML('<p class="section-label">All Support Tickets</p>')
                with gr.Column(scale=1, min_width=140):
                    refresh_btn = gr.Button("🔄 Refresh", elem_classes=["btn-search"])

            gr.HTML('<hr class="divider">')
            tickets_output = gr.HTML(
                value=render_tickets(),
                elem_classes=["faq-results"]
            )

            refresh_btn.click(fn=render_tickets, outputs=[tickets_output])

    # ── Agent Event Handlers ────────────────────────────────────────
    submit_btn.click(fn=process_query, inputs=[query_input], outputs=[category_out, sentiment_out, response_out, results_block, tickets_output])
    query_input.submit(fn=process_query, inputs=[query_input], outputs=[category_out, sentiment_out, response_out, results_block, tickets_output])
    clear_btn.click(fn=clear_all, inputs=[], outputs=[query_input, category_out, sentiment_out, response_out, results_block])

    # ── FAQ Event Handlers ──────────────────────────────────────────
    faq_search_btn.click(fn=lambda s: search_faqs(s, "All"),   inputs=[faq_search], outputs=[faq_output])
    faq_search.submit(fn=lambda s: search_faqs(s, "All"),      inputs=[faq_search], outputs=[faq_output])
    faq_cat_all.click(fn=lambda: search_faqs("", "All"),       outputs=[faq_output])
    faq_cat_technical.click(fn=lambda: search_faqs("", "Technical"), outputs=[faq_output])
    faq_cat_billing.click(fn=lambda: search_faqs("", "Billing"),     outputs=[faq_output])
    faq_cat_general.click(fn=lambda: search_faqs("", "General"),     outputs=[faq_output])


# triage_agent.py
# ── Triage Agent (separated into its own file) ─────────────────────
from langchain_core.prompts import ChatPromptTemplate
from state import State
from llm import llm


def triage_agent(state: State) -> State:
    """
    Classifies the query by category and sentiment.
    Acts as the single entry point — routes everything.

    Categories:
        Technical  → app/device/software issues
        Billing    → payments, invoices, refunds
        General    → account info, policies, hours
        Web        → needs live / current internet data

    Sentiment:
        Positive / Neutral / Negative
    """
    # ── Step 1: Categorize ─────────────────────────────────────────
    cat_prompt = ChatPromptTemplate.from_template(
        "Categorize the following customer query into EXACTLY one of these categories.\n"
        "Reply with ONLY the category name, nothing else.\n"
        "Categories: Technical, Billing, General, Web\n\n"
        "Use 'Web' ONLY if the query needs live/current internet data.\n\n"
        "Query: {query}\n\n"
        "Category:"
    )
    raw_category = (cat_prompt | llm).invoke({"query": state["query"]}).content.strip()

    # Normalise — LLMs sometimes wrap the word in extra text
    category = "General"  # default
    for cat in ["Technical", "Billing", "General", "Web"]:
        if cat.lower() in raw_category.lower():
            category = cat
            break

    # ── Step 2: Sentiment ──────────────────────────────────────────
    sent_prompt = ChatPromptTemplate.from_template(
        "Classify the sentiment of this customer query.\n"
        "Reply with ONLY one word: Positive, Neutral, or Negative.\n\n"
        "Query: {query}\n\n"
        "Sentiment:"
    )
    raw_sentiment = (sent_prompt | llm).invoke({"query": state["query"]}).content.strip()

    sentiment = "Neutral"  # default
    for s in ["Positive", "Neutral", "Negative"]:
        if s.lower() in raw_sentiment.lower():
            sentiment = s
            break

    print(f"[Triage] category={category}  sentiment={sentiment}")
    return {
        "category":  category,
        "sentiment": sentiment,
        "resolved":  False,
    }

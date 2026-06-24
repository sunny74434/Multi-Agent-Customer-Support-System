import chromadb
from chromadb.utils import embedding_functions
from langchain_core.prompts import ChatPromptTemplate

from faq import FAQ_DATA  # single source of truth for FAQ content

# ── ChromaDB client & collection ──────────────────────────────────
_client = chromadb.PersistentClient(path="./chroma_db")

_embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = _client.get_or_create_collection(
    name="faqs",
    embedding_function=_embedder,
)


# ── Load FAQs from faq.py into ChromaDB (idempotent) ─────────────
def load_faqs() -> None:
    """
    Reads FAQ_DATA from faq.py and upserts every Q/A pair into the
    'faqs' ChromaDB collection.  Skips if the collection is already
    populated so startup is fast on subsequent runs.
    """
    if collection.count() > 0:
        print(f"[ChromaDB] Collection already has {collection.count()} FAQs — skipping reload.")
        return

    docs, ids, metas = [], [], []
    idx = 0
    for category, items in FAQ_DATA.items():
        for item in items:
            # Store both Q and A together so semantic search can match
            # on either the question wording or key answer terms.
            docs.append(f"Q: {item['q']}\nA: {item['a']}")
            ids.append(f"faq_{idx}")
            metas.append({
                "category": category,
                "question": item["q"],
            })
            idx += 1

    collection.add(documents=docs, ids=ids, metadatas=metas)
    print(f"[ChromaDB] Loaded {idx} FAQs from faq.py ✅")


# ── Raw semantic search (used internally) ─────────────────────────
def _raw_search(query: str, n_results: int = 3) -> dict:
    """
    Returns the raw ChromaDB query result including distances so we
    can apply a confidence threshold.
    """
    return collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count() or 1),
        include=["documents", "distances", "metadatas"],
    )


# ── Public: plain text FAQ context (for display / agents) ─────────
def search_faq_chroma(query: str, n_results: int = 2) -> str:
    """
    Returns the top-N matching FAQ chunks as plain text.
    Used by the faq_kb_retrieval agent to feed context to the LLM.
    """
    results = _raw_search(query, n_results)
    docs = results["documents"][0]
    if not docs:
        return "No relevant FAQs found."
    return "\n\n---\n\n".join(docs)


# ─────────────────────────────────────────────────────────────────
# MAIN PUBLIC FUNCTION
# ─────────────────────────────────────────────────────────────────
# FAQ_CONFIDENCE_THRESHOLD:
#   ChromaDB uses cosine distance (0 = perfect match, 2 = opposite).
#   A distance ≤ 0.45 is a strong semantic match → serve directly.
#   Anything higher means the FAQ didn't really match → fall to LLM.
FAQ_CONFIDENCE_THRESHOLD = 0.45


def rag_resolve(query: str, llm) -> dict:
    """
    Three-tier RAG pipeline.

    Returns a dict:
        {
            "resolved":     bool,
            "answer":       str,
            "source":       "faq" | "llm" | "escalate",
            "faq_context":  str,   # raw FAQ text used (may be empty)
        }

    Usage in agents.py:
        from chroma_store import rag_resolve
        result = rag_resolve(state["query"], llm)
        # result["resolved"] tells the router what to do next
    """
    # ── Tier 1: FAQ semantic search ────────────────────────────────
    raw = _raw_search(query, n_results=3)
    docs      = raw["documents"][0]
    distances = raw["distances"][0]

    # Build human-readable FAQ context string
    faq_context = "\n\n---\n\n".join(docs) if docs else ""

    best_distance = distances[0] if distances else 999.0
    print(f"[RAG] Best FAQ distance={best_distance:.3f}  threshold={FAQ_CONFIDENCE_THRESHOLD}")

    if best_distance <= FAQ_CONFIDENCE_THRESHOLD and docs:
        # High-confidence FAQ hit — answer directly from KB
        top_doc = docs[0]
        # Extract the answer part (everything after "A: ")
        if "\nA: " in top_doc:
            answer = top_doc.split("\nA: ", 1)[1].strip()
        else:
            answer = top_doc.strip()

        print(f"[RAG] ✅ Tier 1 — answered from FAQ")
        return {
            "resolved":    True,
            "answer":      answer,
            "source":      "faq",
            "faq_context": faq_context,
        }

    # ── Tier 2: LLM fallback using FAQ context as hints ───────────
    print(f"[RAG] ⚠️  Tier 2 — FAQ confidence too low, falling back to LLM")

    llm_prompt = ChatPromptTemplate.from_template(
        "You are a customer support agent.\n\n"
        "The following knowledge-base snippets may or may not be relevant:\n"
        "{faq_context}\n\n"
        "Customer query: {query}\n\n"
        "Using the snippets above AND your own knowledge, can you resolve "
        "this query with confidence?\n\n"
        "If YES — reply starting with exactly 'RESOLVED:' followed by your answer.\n"
        "If NO  — reply starting with exactly 'UNRESOLVED:' followed by the reason.\n\n"
        "Your response (must start with RESOLVED: or UNRESOLVED:):"
    )

    llm_result = (llm_prompt | llm).invoke({
        "query":       query,
        "faq_context": faq_context or "No relevant FAQ articles found.",
    }).content.strip()

    low = llm_result.lower()

    if "unresolved:" in low:
        idx = low.index("unresolved:")
        reason = llm_result[idx + 11:].strip()
        print(f"[RAG] ❌ Tier 3 — LLM also unresolved → escalate")
        return {
            "resolved":    False,
            "answer":      reason,
            "source":      "escalate",
            "faq_context": faq_context,
        }

    elif "resolved:" in low:
        idx = low.index("resolved:")
        answer = llm_result[idx + 9:].strip()
        print(f"[RAG] ✅ Tier 2 — answered by LLM fallback")
        return {
            "resolved":    True,
            "answer":      answer,
            "source":      "llm",
            "faq_context": faq_context,
        }

    else:
        # LLM answered directly without a prefix — treat as resolved
        print(f"[RAG] ✅ Tier 2 — LLM answered (no prefix)")
        return {
            "resolved":    True,
            "answer":      llm_result,
            "source":      "llm",
            "faq_context": faq_context,
        }


# ── Auto-load FAQs from faq.py on import ──────────────────────────
load_faqs()

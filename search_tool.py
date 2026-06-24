# search_tool.py
import os
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv()

_api_key = os.environ.get("TAVILY_API_KEY")  # no default value
if not _api_key:
    raise EnvironmentError(
        "TAVILY_API_KEY is not set.\n"
        "  • Locally: copy .env.example → .env and fill in your key.\n"
        "  • GitHub Actions / server: add it as a repository secret / env var."
    )

os.environ["TAVILY_API_KEY"] = _api_key
tavily_tool = TavilySearchResults(max_results=3)


def run_web_search(query: str) -> str:
    try:
        results = tavily_tool.invoke({"query": query})
        if not results:
            return "No web results found."

        formatted = ""
        for i, r in enumerate(results, 1):
            formatted += f"[{i}] {r.get('title', 'No title')}\n"
            formatted += f"    URL: {r.get('url', '')}\n"
            formatted += f"    {r.get('content', '')}\n\n"
        return formatted.strip()

    except Exception as e:
        return f"Web search failed: {str(e)}"






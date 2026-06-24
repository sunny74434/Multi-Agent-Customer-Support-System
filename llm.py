
# llm.py
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

_api_key = os.environ.get("GROQ_API_KEY")  # no default value
if not _api_key:
    raise EnvironmentError(
        "GROQ_API_KEY is not set.\n"
        "  • Locally: copy .env.example → .env and fill in your key.\n"
        "  • GitHub Actions / server: add it as a repository secret / env var."
    )

llm = ChatGroq(
    temperature=0,
    groq_api_key=_api_key,
    model_name="llama-3.3-70b-versatile",
)
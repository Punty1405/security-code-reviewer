import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# LangSmith
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "security-code-reviewer")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment")

if LANGCHAIN_TRACING_V2=='true' and not LANGCHAIN_API_KEY:
    raise ValueError("Warning: LangSmith tracing enabled but LANGCHAIN_API_KEY not set")
"""Configuration and environment variables for swarmtip."""
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_MODEL = "gemini-3.5-flash"
EDGE_MIN = 0.03
BEST_THIRD_POINTS = 4

# DB settings
CLICKHOUSE_HOST = os.environ.get("CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_PORT = int(os.environ.get("CLICKHOUSE_PORT", "8443" if os.environ.get("CLICKHOUSE_SECURE", "false").lower() in ("1", "true", "yes") else "8123"))
CLICKHOUSE_SECURE = os.environ.get("CLICKHOUSE_SECURE", "false").lower() in ("1", "true", "yes")
CLICKHOUSE_USER = os.environ.get("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.environ.get("CLICKHOUSE_PASSWORD", "")
CLICKHOUSE_DATABASE = os.environ.get("CLICKHOUSE_DATABASE", "default")

# API Keys
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", os.environ.get("GEMINI_API", ""))

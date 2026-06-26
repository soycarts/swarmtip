"""Shared ClickHouse client using config.py settings."""
import clickhouse_connect
import config

_client = None

def client():
    """Lazily build and cache the ClickHouse client."""
    global _client
    if _client is None:
        _client = clickhouse_connect.get_client(
            host=config.CLICKHOUSE_HOST,
            port=config.CLICKHOUSE_PORT,
            username=config.CLICKHOUSE_USER,
            password=config.CLICKHOUSE_PASSWORD,
            secure=config.CLICKHOUSE_SECURE,
            database=config.CLICKHOUSE_DATABASE,
        )
    return _client

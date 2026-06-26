import modal
import os
import subprocess

image = modal.Image.debian_slim().pip_install([
    "fastapi",
    "uvicorn",
    "clickhouse-connect",
    "tavily-python",
    "google-genai",
    "python-dotenv"
])

app = modal.App("swarmtip-orchestrator")

@app.function(
    image=image,
    schedule=modal.Cron("* * * * *"),
    secrets=[modal.Secret.from_dotenv()]
)
def run_orchestrator():
    from orchestrator import run_loop
    import asyncio
    
    # We will modify run_loop to exit after 30 seconds to prevent infinite billing,
    # or just let it run. But since Modal cron functions shouldn't overlap excessively,
    # it's best if we just run it with a timeout.
    try:
        asyncio.run(asyncio.wait_for(run_loop(), timeout=45.0))
    except asyncio.TimeoutError:
        print("Orchestrator completed its 45-second heartbeat cycle.")

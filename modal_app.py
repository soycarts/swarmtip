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
]).add_local_dir(".", remote_path="/app")

app = modal.App("swarmtip-orchestrator")

@app.function(
    image=image,
    schedule=modal.Cron("* * * * *"),
    secrets=[modal.Secret.from_dotenv()]
)
def run_orchestrator():
    import sys
    import os
    print("SYS PATH:", sys.path)
    print("CWD:", os.getcwd())
    if os.path.exists("/app"):
        print("CONTENTS OF /app:", os.listdir("/app"))
    else:
        print("/app DOES NOT EXIST")
    
    sys.path.insert(0, "/app")
    from orchestrator import run_loop
    import asyncio
    
    # We will modify run_loop to exit after 30 seconds to prevent infinite billing,
    # or just let it run. But since Modal cron functions shouldn't overlap excessively,
    # it's best if we just run it with a timeout.
    try:
        asyncio.run(asyncio.wait_for(run_loop(), timeout=45.0))
    except asyncio.TimeoutError:
        print("Orchestrator completed its 45-second heartbeat cycle.")

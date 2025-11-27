import time
from datetime import datetime

LOG_PATH = "logs/requests.log"


def log_request(question, mode, cache_hit, latency):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    entry = (
        f"{timestamp} | "
        f"mode={mode} | "
        f"pathway=RAG | "
        f"cache={cache_hit} | "
        f"latency={latency:.3f}s | "
        f"question=\"{question}\"\n"
    )

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry)

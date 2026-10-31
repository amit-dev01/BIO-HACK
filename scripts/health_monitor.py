"""Live health monitoring script for CanopyAI backend during hackathon presentation.

Continuously monitors latency, uptime, external services, and resource utilization.
"""

import argparse
from datetime import datetime, timezone
import json
import logging
import os
import sys
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("canopyai.monitor")


def monitor_health(base_url: str = "http://localhost:8000", interval_seconds: int = 5, loop: bool = False) -> bool:
    """Query /api/health and report diagnostics."""
    logger.info("Connecting to CanopyAI Health Monitor at %s (interval: %ds)", base_url, interval_seconds)

    while True:
        try:
            t0 = time.time()
            with httpx.Client(base_url=base_url, timeout=5.0) as client:
                res = client.get("/api/health")
                latency_ms = (time.time() - t0) * 1000

            if res.status_code == 200:
                data = res.json()
                status_str = data.get("status", "unknown").upper()
                uptime = data.get("uptime_seconds", 0)
                services = data.get("services", {})
                ee_status = services.get("earth_engine", {}).get("status") or data.get("earth_engine", "n/a")
                db_status = services.get("database", {}).get("status") or data.get("database", "n/a")
                system = data.get("system", {})
                cpu = system.get("cpu_percent", 0.0)
                mem = system.get("memory_percent", 0.0)

                log_fn = logger.info if status_str == "OK" else logger.warning
                log_fn(
                    "STATUS: %s | Latency: %.1fms | Uptime: %.1fs | EE: %s | DB: %s | CPU: %.1f%% | RAM: %.1f%%",
                    status_str,
                    latency_ms,
                    uptime,
                    ee_status,
                    db_status,
                    cpu,
                    mem,
                )
            else:
                logger.error("Health check failed with status code %d: %s", res.status_code, res.text)
        except Exception as e:
            logger.error("Connection to %s failed: %s", base_url, e)

        if not loop:
            break
        time.sleep(interval_seconds)

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CanopyAI Health Monitor CLI")
    parser.add_argument("--url", default="http://localhost:8000", help="Base backend URL")
    parser.add_argument("--interval", type=int, default=5, help="Polling interval in seconds")
    parser.add_argument("--continuous", action="store_true", help="Run polling continuously")
    args = parser.parse_args()

    monitor_health(base_url=args.url, interval_seconds=args.interval, loop=args.continuous)

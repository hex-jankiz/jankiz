"""
Jankiz Telegram Bot - High-Availability 24/7 Watchdog Supervisor
===============================================================
Ensures the bot stays online 24/7 ("لا ينام") by monitoring the process
and automatically recovering/restarting upon any network drops or crashes.
"""

import sys
import os
import time
import subprocess
from pathlib import Path
from datetime import datetime

CURRENT_DIR = Path(__file__).resolve().parent
BOT_SCRIPT = CURRENT_DIR / "bot.py"
LOG_FILE = CURRENT_DIR / "supervisor.log"

def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [Supervisor] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def run_watchdog():
    log("======================================================")
    log("  Starting Jankiz 24/7 High-Availability Supervisor   ")
    log("======================================================")

    restarts = 0
    max_fast_restarts = 5
    backoff = 3

    while True:
        log(f"Launching bot process (Attempt #{restarts + 1})...")
        start_time = time.time()
        
        try:
            # Spawn bot process
            proc = subprocess.Popen(
                [sys.executable, str(BOT_SCRIPT)],
                cwd=str(CURRENT_DIR)
            )
            # Wait for bot process
            exit_code = proc.wait()
            duration = time.time() - start_time

            log(f"Bot process exited with code {exit_code} (Ran for {duration:.1f}s)")
            
            # If it ran for more than 5 minutes, reset restart counter
            if duration > 300:
                restarts = 0

            restarts += 1

            if restarts > max_fast_restarts:
                log(f"Too many quick restarts ({restarts}). Cooling down for 30s...")
                time.sleep(30)
                restarts = 0
            else:
                log(f"Auto-recovering in {backoff} seconds...")
                time.sleep(backoff)

        except KeyboardInterrupt:
            log("Manual shutdown requested. Terminating bot...")
            try:
                proc.terminate()
            except Exception:
                pass
            break
        except Exception as e:
            log(f"Supervisor unexpected error: {e}. Retrying in 5s...")
            time.sleep(5)

if __name__ == "__main__":
    run_watchdog()

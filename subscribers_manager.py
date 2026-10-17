"""
Jankiz Telegram Bot - Subscribers & Automated Broadcast Manager
==============================================================
Manages subscribers for automated programming news broadcasts.
"""

import json
from pathlib import Path
from typing import Set

DATA_FILE = Path(__file__).resolve().parent / "subscribers.json"

def load_subscribers() -> Set[int]:
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data.get("subscribers", []))
        except Exception:
            pass
    return set()

def save_subscribers(subs: Set[int]):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"subscribers": list(subs)}, f, indent=2)
    except Exception as e:
        print(f"[Subscribers] Error saving subscribers: {e}")

def add_subscriber(chat_id: int) -> bool:
    subs = load_subscribers()
    if chat_id not in subs:
        subs.add(chat_id)
        save_subscribers(subs)
        return True
    return False

def remove_subscriber(chat_id: int) -> bool:
    subs = load_subscribers()
    if chat_id in subs:
        subs.remove(chat_id)
        save_subscribers(subs)
        return True
    return False

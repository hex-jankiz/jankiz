"""
Jankiz Telegram Bot - Security & Hardening Engine
================================================
- Anti-Spam / Rate Limiting (Token Bucket per User)
- Input Sanitization & HTML Escaping
- Secure Error Shielding & Anomaly Detection
"""

import time
import html
from typing import Dict, Tuple

class RateLimiter:
    """Sliding-window rate limiter per Telegram user to prevent spam and DDoS."""
    
    def __init__(self, max_requests: int = 15, window_seconds: int = 30):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.user_history: Dict[int, list] = {}
        self.banned_users: Dict[int, float] = {}

    def is_allowed(self, user_id: int) -> Tuple[bool, str]:
        now = time.time()
        
        # Check temporary ban
        if user_id in self.banned_users:
            ban_expiry = self.banned_users[user_id]
            if now < ban_expiry:
                remaining = int(ban_expiry - now)
                return False, f"⚠️ تم تقييد حسابك مؤقتاً لحماية الخادم بسبب كثرة الطلبات. يرجى الانتظار {remaining} ثانية."
            else:
                del self.banned_users[user_id]
                self.user_history[user_id] = []

        history = self.user_history.get(user_id, [])
        # Prune old timestamps
        history = [t for t in history if now - t < self.window_seconds]
        
        if len(history) >= self.max_requests:
            # Trigger temporary cooldown
            self.banned_users[user_id] = now + 45  # 45 seconds cooldown
            return False, "⚠️ تم تفعيل نظام الحماية ضد الإغراق (Anti-Flood). يرجى التمهل 45 ثانية قبل إرسال أوامر جديدة."

        history.append(now)
        self.user_history[user_id] = history
        return True, ""

def sanitize_text(text: str) -> str:
    """Safely escape text for Telegram HTML mode to avoid parse crashes."""
    if not text:
        return ""
    return html.escape(str(text))

# Global rate limiter instance
limiter = RateLimiter(max_requests=12, window_seconds=20)

"""
Jankiz Telegram Bot - Database Storage Engine
============================================
SQLite persistent storage for:
- Users & profile metadata
- Category-based subscription preferences
- Verified programming news & articles
- Verified real GitHub repositories
- Social media platform updates & outage statuses
- Broadcast delivery logging to prevent duplicates
"""

import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Set

DB_PATH = Path(__file__).resolve().parent / "jankiz.db"

def get_connection():
    conn = sqlite3.connect(str(DB_PATH), timeout=15)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Users
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 2. Subscriptions
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_subscriptions (
            user_id INTEGER,
            category TEXT,
            subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, category)
        );
        """)

        # 3. Articles (News, AI, Tech, Security)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash_id TEXT UNIQUE,
            category TEXT,
            title TEXT,
            description TEXT,
            why_useful TEXT,
            url TEXT,
            source TEXT,
            published_at TEXT,
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            verified INTEGER DEFAULT 1
        );
        """)

        # 4. GitHub Projects
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS github_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_full_name TEXT UNIQUE,
            name TEXT,
            description TEXT,
            language TEXT,
            stars TEXT,
            forks TEXT,
            updated_at TEXT,
            why_useful TEXT,
            quickstart TEXT,
            url TEXT,
            category TEXT,
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            verified INTEGER DEFAULT 1
        );
        """)

        # 5. Social Media Updates & Outages
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS social_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash_id TEXT UNIQUE,
            platform TEXT,
            title TEXT,
            status TEXT,
            details TEXT,
            date TEXT,
            source_url TEXT,
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            verified INTEGER DEFAULT 1
        );
        """)

        # 6. Broadcast Log (prevents sending same content to same user)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS broadcast_log (
            user_id INTEGER,
            content_type TEXT,
            content_id INTEGER,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, content_type, content_id)
        );
        """)

        # 7. System Settings
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_cat ON articles(category);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_github_cat ON github_projects(category);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_social_plat ON social_updates(platform);")

        conn.commit()

# --- User & Subscription Management ---

def register_user(user_id: int, username: Optional[str], first_name: Optional[str]):
    with get_connection() as conn:
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
        INSERT INTO users (user_id, username, first_name, last_active)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            first_name = excluded.first_name,
            last_active = excluded.last_active
        """, (user_id, username, first_name, now))
        conn.commit()

def get_user_subscriptions(user_id: int) -> Set[str]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT category FROM user_subscriptions WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        return {r["category"] for r in rows}

def set_user_subscription(user_id: int, category: str, enabled: bool) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        if enabled:
            cursor.execute("""
            INSERT OR IGNORE INTO user_subscriptions (user_id, category)
            VALUES (?, ?)
            """, (user_id, category))
        else:
            cursor.execute("DELETE FROM user_subscriptions WHERE user_id = ? AND category = ?", (user_id, category))
        conn.commit()
        return True

def get_subscribers_for_category(category: str) -> List[int]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM user_subscriptions WHERE category = ?", (category,))
        return [r["user_id"] for r in cursor.fetchall()]

def count_all_users() -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM users")
        row = cursor.fetchone()
        return row["cnt"] if row else 0

# --- Articles Management ---

def compute_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

def save_article(category: str, title: str, description: str, url: str, source: str,
                 why_useful: str = "", published_at: str = "") -> bool:
    h = compute_hash(url or title)
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO articles (hash_id, category, title, description, why_useful, url, source, published_at, verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (h, category, title, description, why_useful, url, source, published_at))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def get_latest_articles(category: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        if category and category != "all":
            cursor.execute("""
            SELECT * FROM articles WHERE category = ? ORDER BY id DESC LIMIT ?
            """, (category, limit))
        else:
            cursor.execute("""
            SELECT * FROM articles ORDER BY id DESC LIMIT ?
            """, (limit,))
        return [dict(r) for r in cursor.fetchall()]

# --- GitHub Projects Management ---

def save_github_project(repo_full_name: str, name: str, description: str, language: str,
                        stars: str, forks: str, updated_at: str, why_useful: str,
                        quickstart: str, url: str, category: str = "general") -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO github_projects
            (repo_full_name, name, description, language, stars, forks, updated_at, why_useful, quickstart, url, category, verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            ON CONFLICT(repo_full_name) DO UPDATE SET
                description = excluded.description,
                stars = excluded.stars,
                forks = excluded.forks,
                updated_at = excluded.updated_at,
                why_useful = excluded.why_useful,
                quickstart = excluded.quickstart
            """, (repo_full_name, name, description, language, stars, forks, updated_at, why_useful, quickstart, url, category))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def get_latest_github_projects(category: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        if category and category != "all":
            cursor.execute("""
            SELECT * FROM github_projects WHERE category = ? ORDER BY id DESC LIMIT ?
            """, (category, limit))
        else:
            cursor.execute("""
            SELECT * FROM github_projects ORDER BY id DESC LIMIT ?
            """, (limit,))
        return [dict(r) for r in cursor.fetchall()]

# --- Social Updates Management ---

def save_social_update(platform: str, title: str, status: str, details: str, date: str, source_url: str) -> bool:
    h = compute_hash(f"{platform}_{title}_{date}")
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO social_updates (hash_id, platform, title, status, details, date, source_url, verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """, (h, platform, title, status, details, date, source_url))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def get_latest_social_updates(platform: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        if platform and platform != "all":
            cursor.execute("""
            SELECT * FROM social_updates WHERE LOWER(platform) = LOWER(?) ORDER BY id DESC LIMIT ?
            """, (platform, limit))
        else:
            cursor.execute("""
            SELECT * FROM social_updates ORDER BY id DESC LIMIT ?
            """, (limit,))
        return [dict(r) for r in cursor.fetchall()]

# --- Broadcast Logging ---

def is_broadcasted(user_id: int, content_type: str, content_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT 1 FROM broadcast_log WHERE user_id = ? AND content_type = ? AND content_id = ?
        """, (user_id, content_type, content_id))
        return cursor.fetchone() is not None

def log_broadcast(user_id: int, content_type: str, content_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT OR IGNORE INTO broadcast_log (user_id, content_type, content_id)
        VALUES (?, ?, ?)
        """, (user_id, content_type, content_id))
        conn.commit()

# --- System Stats for Admin ---

def get_system_stats() -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as c FROM users")
        total_users = cursor.fetchone()["c"]
        cursor.execute("SELECT COUNT(DISTINCT user_id) as c FROM user_subscriptions")
        total_subscribers = cursor.fetchone()["c"]
        cursor.execute("SELECT COUNT(*) as c FROM articles")
        total_articles = cursor.fetchone()["c"]
        cursor.execute("SELECT COUNT(*) as c FROM github_projects")
        total_github = cursor.fetchone()["c"]
        cursor.execute("SELECT COUNT(*) as c FROM social_updates")
        total_social = cursor.fetchone()["c"]
        cursor.execute("SELECT COUNT(*) as c FROM broadcast_log")
        total_broadcasts = cursor.fetchone()["c"]

        return {
            "total_users": total_users,
            "total_subscribers": total_subscribers,
            "total_articles": total_articles,
            "total_github_projects": total_github,
            "total_social_updates": total_social,
            "total_broadcasts": total_broadcasts
        }

# Initialize database on module import
init_db()

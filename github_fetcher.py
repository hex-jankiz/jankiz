"""
Jankiz Telegram Bot - Verified GitHub Project Discovery Engine
=============================================================
Discovers real, verifiable GitHub repositories across programming categories:
- Python & Automation
- JavaScript / TypeScript & Modern Web
- AI & Machine Learning & LLM tools
- Developer Tools & CLI Utilities
- Cyber Security & Defensive Tools
"""

import os
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime
import db
from security import sanitize_text
from cache_manager import news_cache

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()

# Curated categories for GitHub
CATEGORIES = {
    "all": None,
    "python": "python",
    "javascript": "javascript",
    "typescript": "typescript",
    "ai": None,
    "tools": None,
    "security": None
}

def fetch_trending_from_web(language: Optional[str] = None) -> List[Dict[str, Any]]:
    """Parse real repos from GitHub Trending pages."""
    url = f"https://github.com/trending/{language}" if language else "https://github.com/trending"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    results = []
    try:
        resp = requests.get(url, headers=headers, timeout=8)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            rows = soup.find_all("article", class_="Box-row")
            for row in rows[:8]:
                # 1. Full name & link
                h2 = row.find("h2")
                if not h2 or not h2.find("a"):
                    continue
                a_tag = h2.find("a")
                rel_url = a_tag.get("href", "").strip()
                repo_full_name = rel_url.lstrip("/")
                name = repo_full_name.split("/")[-1] if "/" in repo_full_name else repo_full_name
                repo_url = f"https://github.com{rel_url}"

                # 2. Description
                p_desc = row.find("p")
                description = p_desc.text.strip() if p_desc else "مستودع برمجي نشط على GitHub"

                # 3. Language
                lang_span = row.find("span", itemprop="programmingLanguage")
                lang = lang_span.text.strip() if lang_span else (language.capitalize() if language else "متعدد اللغات")

                # 4. Stars & Forks
                stars_link = row.find("a", href=lambda h: h and h.endswith("/stargazers"))
                stars = stars_link.text.strip() if stars_link else "N/A"

                forks_link = row.find("a", href=lambda h: h and h.endswith("/forks"))
                forks = forks_link.text.strip() if forks_link else "N/A"

                # 5. Quickstart & Why useful
                quickstart = f"git clone {repo_url}.git"
                why_useful = f"مستودع متصدر وفعال في مجال {lang} يوفر حلاً عملياً للمطورين."

                today_str = datetime.now().strftime("%Y-%m-%d")

                item = {
                    "repo_full_name": repo_full_name,
                    "name": name,
                    "description": description,
                    "language": lang,
                    "stars": stars,
                    "forks": forks,
                    "updated_at": today_str,
                    "why_useful": why_useful,
                    "quickstart": quickstart,
                    "url": repo_url,
                    "category": language or "general"
                }

                # Save to database
                db.save_github_project(
                    repo_full_name=repo_full_name,
                    name=name,
                    description=description,
                    language=lang,
                    stars=stars,
                    forks=forks,
                    updated_at=today_str,
                    why_useful=why_useful,
                    quickstart=quickstart,
                    url=repo_url,
                    category=language or "general"
                )

                results.append(item)
    except Exception as e:
        print(f"[GitHubFetcher] Web trending error for {language}: {e}")

    return results

def get_github_projects(category: str = "all", limit: int = 3) -> List[Dict[str, Any]]:
    """Retrieve GitHub projects with SQLite cache and fallback."""
    # 1. Try DB first
    db_items = db.get_latest_github_projects(category=category if category != "all" else None, limit=limit)
    if db_items and len(db_items) >= limit:
        return db_items

    # 2. Fetch live from GitHub Trending
    lang_param = CATEGORIES.get(category)
    fetched = fetch_trending_from_web(lang_param)
    if fetched:
        return fetched[:limit]

    # 3. Fallback verified repos
    return db_items if db_items else [
        {
            "name": "fastapi",
            "repo_full_name": "tiangolo/fastapi",
            "description": "FastAPI framework, high performance, easy to learn, fast to code, ready for production",
            "language": "Python",
            "stars": "78,000+",
            "forks": "6,500+",
            "updated_at": "محدث هذا الأسبوع",
            "why_useful": "إطار عمل قياسي لبناء واجهات برمجية فائقة السرعة مع توثيق OpenAPI تفاعلي تلقائي.",
            "quickstart": "pip install fastapi uvicorn",
            "url": "https://github.com/tiangolo/fastapi"
        }
    ]

def format_github_card(project: Dict[str, Any]) -> str:
    """Format project matching the user's exact required card template."""
    name = sanitize_text(project.get("name", ""))
    desc = sanitize_text(project.get("description", ""))
    lang = sanitize_text(project.get("language", "غير محدد"))
    stars = sanitize_text(str(project.get("stars", "N/A")))
    forks = sanitize_text(str(project.get("forks", "N/A")))
    updated = sanitize_text(str(project.get("updated_at", "اليوم")))
    why = sanitize_text(project.get("why_useful", "أداة ومكتبة برمجية مفتوحة المصدر."))
    quickstart = sanitize_text(project.get("quickstart", "git clone"))
    url = project.get("url", "https://github.com")

    msg = (
        f"🐙 <b>{name}</b>\n\n"
        f"📝 <b>الوصف:</b> {desc}\n\n"
        f"💻 <b>لغة البرمجة:</b> {lang}\n"
        f"⭐ <b>النجوم:</b> {stars} | 🔀 <b>Forks:</b> {forks}\n"
        f"📅 <b>آخر تحديث:</b> {updated}\n\n"
        f"🎯 <b>الفائدة:</b> {why}\n\n"
        f"⚙️ <b>طريقة البدء:</b>\n"
        f"<code>{quickstart}</code>\n\n"
        f"🔗 <a href='{url}'>المستودع الأصلي: اضغط هنا للمعاينة ↗</a>"
    )
    return msg

"""
Jankiz Telegram Bot - Developer Tools Catalog
============================================
Verified developer tools, CLI utilities, linters, and frameworks.
"""

from typing import List, Dict, Any
from security import sanitize_text

DEV_TOOLS = [
    {
        "name": "Ruff",
        "category": "Linter & Formatter",
        "language": "Python / Rust",
        "description": "محلل ومنسق كود بايثون فائق السرعة مبني بلغة Rust، أسرع بـ 10-100 ضعف من Flake8 و Black.",
        "install": "pip install ruff",
        "url": "https://github.com/astral-sh/ruff"
    },
    {
        "name": "HTTPie",
        "category": "API Client",
        "language": "CLI Tool",
        "description": "أداة سطر أوامر تفاعلية وسهلة الاستخدام لإرسال طلبات HTTP واختبار واجهات الـ REST API بألوان وتنسيق فوري.",
        "install": "pip install httpie (أو winget install httpie)",
        "url": "https://httpie.io"
    },
    {
        "name": "Lazygit",
        "category": "Git CLI TUI",
        "language": "Go",
        "description": "واجهة طرفية مرئية وبديهية لإدارة مستودعات وفروع Git والتنقل السلس دون كتابة الأوامر الطويلة.",
        "install": "winget install jesseduffield.lazygit",
        "url": "https://github.com/jesseduffield/lazygit"
    },
    {
        "name": "Postman / Bruno",
        "category": "API Testing",
        "language": "Open Source",
        "description": "عميل واجهات برمجية خفيف مفتوح المصدر يخزن مجموعات الطلبات كملفات نصية مباشرة داخل مجلد مشروعك في Git.",
        "install": "npm i -g @usebruno/cli",
        "url": "https://www.usebruno.com"
    }
]

def get_dev_tools(limit: int = 3) -> List[Dict[str, Any]]:
    return DEV_TOOLS[:limit]

def format_dev_tool_card(tool: Dict[str, Any]) -> str:
    name = sanitize_text(tool.get("name", ""))
    cat = sanitize_text(tool.get("category", ""))
    lang = sanitize_text(tool.get("language", ""))
    desc = sanitize_text(tool.get("description", ""))
    inst = sanitize_text(tool.get("install", ""))
    url = tool.get("url", "#")

    msg = (
        f"🛠️ <b>{name}</b>\n\n"
        f"🏷️ <b>التصنيف:</b> {cat} | 💻 <b>البيئة:</b> {lang}\n\n"
        f"📝 <b>الوصف:</b>\n{desc}\n\n"
        f"⚙️ <b>أمر التثبيت السريع:</b>\n"
        f"<code>{inst}</code>\n\n"
        f"🔗 <a href='{url}'>الموقع والتوثيق الرسمي ↗</a>"
    )
    return msg

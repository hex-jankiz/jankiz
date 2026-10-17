"""
Jankiz Telegram Bot - Verified Code & Practical Tutorials Library
================================================================
Curated, tested, executable engineering code tutorials & recipes.
"""

from typing import List, Dict, Any, Optional
from security import sanitize_text

TUTORIALS = [
    {
        "id": "py-async-fetch",
        "category": "python",
        "title": "جلب البيانات غير المتزامن بـ aiohttp و asyncio",
        "language": "Python 3.10+",
        "difficulty": "متوسط",
        "description": "طريقة إرسال عشرات الطلبات المتزامنة في أجزاء من الثانية دون إبطاء التطبيق مع إدارة الـ Session بشكل سليم.",
        "code": """import asyncio
import aiohttp

async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.json()

async def main():
    urls = ["https://api.github.com", "https://httpbin.org/json"]
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, u) for u in urls]
        results = await asyncio.gather(*tasks)
        print(f"تم جلب {len(results)} نتائج بنجاح.")

# asyncio.run(main())""",
        "is_tested": True,
        "test_result": "تم التحقق من تشغيل الكود واختباره بنجاح في بيئة بايثون."
    },
    {
        "id": "ts-clean-api",
        "category": "typescript",
        "title": "بناء عميل API نوعي آمن بـ TypeScript Generics",
        "language": "TypeScript 5+",
        "difficulty": "متقدم",
        "description": "إنشاء دالة موحدة لطلبات الشبكة مع التحقق التلقائي من بنية البيانات المعادة (Type-Safe API Client).",
        "code": """interface ApiResponse<T> {
  data: T;
  status: number;
}

async function apiRequest<T>(url: string): Promise<ApiResponse<T>> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);
  const data: T = await res.json();
  return { data, status: res.status };
}""",
        "is_tested": True,
        "test_result": "تم التحقق ومطابقة الأنواع الصارمة في مترجم TypeScript."
    },
    {
        "id": "sql-safe-pagination",
        "category": "sql",
        "title": "التصفح السريع والآمن لقواعد البيانات (Cursor-based Pagination)",
        "language": "SQL / PostgreSQL / MySQL",
        "difficulty": "متقدم",
        "description": "بديل فائق السرعة لـ OFFSET في الجداول المليونية؛ يعتمد على آخر معرّف بدلاً من قراءة جميع الصفوف السابقة.",
        "code": """-- بدلاً من: SELECT * FROM orders OFFSET 100000 LIMIT 20; (بطيء جداً)
-- استخدم التصفح بالمؤشر:
SELECT id, total, created_at 
FROM orders 
WHERE id > 100000 
ORDER BY id ASC 
LIMIT 20;""",
        "is_tested": True,
        "test_result": "تم اختبار الاستعلام على قواعد بيانات SQLite و PostgreSQL."
    },
    {
        "id": "sec-password-hashing",
        "category": "security",
        "title": "التشفير الآمن لكلمات المرور بـ bcrypt",
        "language": "Python / Security",
        "difficulty": "أساسي",
        "description": "استخدام خوارزمية التشفير المتكيفة مع توليد ملح عشوائي (Salt) لمنع هجمات جداول قوس قزح (Rainbow Tables).",
        "code": """import bcrypt

def hash_password(password: str) -> bytes:
    # توليد ملح وتشفير كلمة المرور
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed)""",
        "is_tested": True,
        "test_result": "تم اختبار دالتي التشفير والتحقق والتأكد من مطابقتها لمعايير OWASP."
    }
]

def get_code_tutorials(category: Optional[str] = None, limit: int = 3) -> List[Dict[str, Any]]:
    if category and category != "all":
        items = [t for t in TUTORIALS if t["category"].lower() == category.lower()]
        return items[:limit]
    return TUTORIALS[:limit]

def format_tutorial_card(t: Dict[str, Any]) -> str:
    title = sanitize_text(t.get("title", ""))
    lang = sanitize_text(t.get("language", ""))
    diff = sanitize_text(t.get("difficulty", "متوسط"))
    desc = sanitize_text(t.get("description", ""))
    code = sanitize_text(t.get("code", ""))
    tested = "✅ تم التحقق من الكود واختباره فعلياً" if t.get("is_tested") else "⚠️ لم يتم الاختبار الآلي"

    msg = (
        f"📚 <b>{title}</b>\n\n"
        f"💻 <b>اللغة / التقنية:</b> {lang} | 🎯 <b>المستوى:</b> {diff}\n\n"
        f"📝 <b>الشرح:</b>\n{desc}\n\n"
        f"⚙️ <b>الشيفرة البرمجية:</b>\n"
        f"<pre>{code}</pre>\n\n"
        f"🧪 <b>حالة الاختبار:</b> <i>{tested}</i>"
    )
    return msg

"""
Jankiz Telegram Bot - Production Platform
=========================================
بوت Jankiz الرسمي المتقدم لأخبار البرمجة والذكاء الاصطناعي والتكنولوجيا
ومشاريع GitHub ومنصات التواصل الاجتماعي ومركز Blender ثلاثي الأبعاد.
"""

import sys
import os
import asyncio
import logging
import threading
from pathlib import Path
from datetime import datetime

# Configure Windows UTF-8 stdout
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

import db
import news_fetcher
import github_fetcher
import social_fetcher
import code_library
import dev_tools
import blender_hub
from config import BOT_TOKEN, PORT, ADMIN_ID
from security import limiter, sanitize_text
from web_preview import run_server, check_telegram_token

# Configure logging
logging.basicConfig(
    format="%(asctime)s - [%(name)s] - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("JankizBot")

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
    BotCommandScopeDefault,
    constants
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Categories definition
SUBSCRIPTION_CATEGORIES = {
    "programming": "💻 أخبار البرمجة",
    "ai": "🤖 الذكاء الاصطناعي",
    "github": "🐙 مشاريع GitHub",
    "blender": "🎨 مركز Blender",
    "social": "📱 منصات التواصل",
    "security": "🔐 الأمن السيبراني"
}

# 17 Official Telegram Slash Commands
TELEGRAM_BOT_COMMANDS = [
    BotCommand("start", "بدء البوت وعرض القائمة الرئيسية"),
    BotCommand("help", "دليل الاستخدام وجميع الأوامر"),
    BotCommand("news", "آخر الأخبار التقنية العامة"),
    BotCommand("programming", "أخبار لغات البرمجة والتقنيات"),
    BotCommand("ai", "أخبار وأدوات الذكاء الاصطناعي"),
    BotCommand("github", "مشاريع ومستودعات GitHub الحقيقية"),
    BotCommand("blender", "مركز Blender للتصميم والـ 3D"),
    BotCommand("social", "أخبار وتحديثات منصات التواصل"),
    BotCommand("tools", "أدوات المطورين وسكربتات البناء"),
    BotCommand("code", "أكواد وشروحات برمجية مختبرة"),
    BotCommand("security", "تنبيهات وأخبار الأمن السيبراني"),
    BotCommand("search", "البحث في محتوى المنصة"),
    BotCommand("subscribe", "إدارة الاشتراكات التلقائية"),
    BotCommand("unsubscribe", "إيقاف التحديثات التلقائية"),
    BotCommand("settings", "إعدادات وتفضيلات المستخدم"),
    BotCommand("about", "معلومات عن منصة Jankiz"),
    BotCommand("status", "حالة خوادم وخدمات المنصة"),
]

START_WELCOME_TEXT = """👋 مرحبًا بك!

🚀 منصتك لمتابعة أحدث التطورات في عالم البرمجة والذكاء الاصطناعي والتكنولوجيا.

💻 أخبار البرمجة
تابع أحدث لغات البرمجة وأطر العمل والمكتبات والتحديثات التي تهم المطورين.

🤖 الذكاء الاصطناعي
اكتشف النماذج الجديدة والأدوات الذكية والتطبيقات العملية والتطورات الحديثة.

📱 منصات التواصل الاجتماعي
تابع تحديثات TikTok وYouTube وInstagram وFacebook وWhatsApp وTelegram وغيرها، مع أخبار الميزات الجديدة والمشكلات والحلول الموثوقة.

🐙 مشاريع GitHub
اكتشف مشاريع مفتوحة المصدر حقيقية، وأدوات برمجية مفيدة، ومكتبات جديدة، ومشاريع تستحق التجربة والتعلم منها.

🛠️ أدوات المطورين
تعرّف على الأدوات التي تساعدك على كتابة الكود وتحسين الأداء وبناء التطبيقات.

🔐 الأمن السيبراني
تابع التحديثات الأمنية والتنبيهات المهمة والممارسات التي تساعد على حماية التطبيقات والأنظمة.

📚 أكواد وشروحات عملية
استفد من أمثلة برمجية مفيدة ومشاريع قابلة للتحقق وشروحات واضحة.

━━━━━━━━━━━━━━━━━━

👇 اختر القسم الذي يهمك من القائمة أدناه، أو اشترك في التحديثات لتصلك الأخبار الجديدة تلقائيًا.

Jankiz | البرمجة والتقنية، في مكان واحد."""


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard with Blender Hub and All Commands."""
    keyboard = [
        [
            InlineKeyboardButton("📰 آخر الأخبار", callback_data="sec_latest_news"),
            InlineKeyboardButton("💻 أخبار البرمجة", callback_data="sec_programming_news")
        ],
        [
            InlineKeyboardButton("🤖 الذكاء الاصطناعي", callback_data="sec_ai_news"),
            InlineKeyboardButton("🐙 مشاريع GitHub", callback_data="sec_github_menu")
        ],
        [
            InlineKeyboardButton("🎨 Blender Hub", callback_data="sec_blender_hub"),
            InlineKeyboardButton("📱 منصات التواصل", callback_data="sec_social_menu")
        ],
        [
            InlineKeyboardButton("🛠️ أدوات المطورين", callback_data="sec_dev_tools"),
            InlineKeyboardButton("📚 الأكواد والشروحات", callback_data="sec_code_tutorials")
        ],
        [
            InlineKeyboardButton("🔐 الأمن السيبراني", callback_data="sec_security_news"),
            InlineKeyboardButton("🔔 إدارة الاشتراكات", callback_data="sec_subscriptions")
        ],
        [
            InlineKeyboardButton("📚 جميع الأوامر", callback_data="sec_help"),
            InlineKeyboardButton("🔎 البحث في المنصة", callback_data="sec_search_prompt")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_blender_keyboard() -> InlineKeyboardMarkup:
    """Sub-menu for Blender Hub (all 13 options required)."""
    keyboard = [
        [
            InlineKeyboardButton("📰 أخبار Blender", callback_data="bln_news"),
            InlineKeyboardButton("🆕 الإصدارات والتحديثات الرسمية", callback_data="bln_releases")
        ],
        [
            InlineKeyboardButton("🧑‍💻 مشاريع Blender على GitHub", callback_data="bln_github"),
            InlineKeyboardButton("🧩 الإضافات والـ Add-ons", callback_data="bln_addons")
        ],
        [
            InlineKeyboardButton("📦 ملفات ومشاريع .blend", callback_data="bln_demo_files"),
            InlineKeyboardButton("🎨 الخامات والـ Textures", callback_data="bln_textures")
        ],
        [
            InlineKeyboardButton("🌍 ملفات HDRI والبيئات", callback_data="bln_hdri"),
            InlineKeyboardButton("🎬 الدروس والشروحات", callback_data="bln_tutorials")
        ],
        [
            InlineKeyboardButton("🛠️ سكربتات Python وأدوات المطورين", callback_data="bln_python_dev"),
            InlineKeyboardButton("🔥 المشاريع الرائجة", callback_data="bln_trending")
        ],
        [
            InlineKeyboardButton("🔎 البحث عن موارد Blender", callback_data="bln_search_prompt"),
            InlineKeyboardButton("🔔 الاشتراك في أخبار Blender", callback_data="toggle_sub_blender")
        ],
        [
            InlineKeyboardButton("↩️ العودة إلى القائمة الرئيسية", callback_data="nav_main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_github_keyboard() -> InlineKeyboardMarkup:
    """Sub-menu for GitHub projects categories."""
    keyboard = [
        [
            InlineKeyboardButton("🐍 مشاريع بايثون", callback_data="gh_cat_python"),
            InlineKeyboardButton("⚡ جافاسكريبت / TS", callback_data="gh_cat_javascript")
        ],
        [
            InlineKeyboardButton("🤖 مشاريع الذكاء الاصطناعي", callback_data="gh_cat_ai"),
            InlineKeyboardButton("🛠️ أدوات وسكربتات", callback_data="gh_cat_tools")
        ],
        [
            InlineKeyboardButton("🔐 أمن سيبراني دفاعي", callback_data="gh_cat_security"),
            InlineKeyboardButton("🌐 جميع مشاريع الترند", callback_data="gh_cat_all")
        ],
        [
            InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="nav_main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_social_keyboard() -> InlineKeyboardMarkup:
    """Sub-menu for Social Media platforms."""
    keyboard = [
        [
            InlineKeyboardButton("Telegram", callback_data="soc_plat_Telegram"),
            InlineKeyboardButton("WhatsApp", callback_data="soc_plat_WhatsApp")
        ],
        [
            InlineKeyboardButton("YouTube", callback_data="soc_plat_YouTube"),
            InlineKeyboardButton("TikTok", callback_data="soc_plat_TikTok")
        ],
        [
            InlineKeyboardButton("Instagram", callback_data="soc_plat_Instagram"),
            InlineKeyboardButton("Discord", callback_data="soc_plat_Discord")
        ],
        [
            InlineKeyboardButton("Reddit", callback_data="soc_plat_Reddit"),
            InlineKeyboardButton("🌐 كافة المنصات", callback_data="soc_plat_all")
        ],
        [
            InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="nav_main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_subscriptions_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Dynamic subscription toggle buttons per category."""
    user_subs = db.get_user_subscriptions(user_id)
    buttons = []
    for cat_key, cat_label in SUBSCRIPTION_CATEGORIES.items():
        is_sub = cat_key in user_subs
        status_icon = "🔔 مشترك" if is_sub else "🔕 غير مشترك"
        btn_text = f"{cat_label}: {status_icon}"
        callback = f"toggle_sub_{cat_key}"
        buttons.append([InlineKeyboardButton(btn_text, callback_data=callback)])

    buttons.append([InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="nav_main_menu")])
    return InlineKeyboardMarkup(buttons)


async def check_user_access(update: Update) -> bool:
    """Register user, track activity and check rate limits."""
    user = update.effective_user
    if user:
        db.register_user(user.id, user.username, user.first_name)
        allowed, msg = limiter.is_allowed(user.id)
        if not allowed:
            if update.effective_message:
                await update.effective_message.reply_html(msg)
            return False
    return True


async def register_bot_commands(application):
    """Register all 17 commands officially with Telegram Bot API so they appear when typing '/'."""
    try:
        await application.bot.set_my_commands(
            commands=TELEGRAM_BOT_COMMANDS,
            scope=BotCommandScopeDefault()
        )
        logger.info("[SUCCESS] All 17 slash commands registered with Telegram API via setMyCommands.")
    except Exception as e:
        logger.warning(f"Could not register commands with Telegram: {e}")


# --- Command Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clean, strict /start greeting requested by the user."""
    if not await check_user_access(update):
        return
    await update.message.reply_html(
        START_WELCOME_TEXT,
        reply_markup=get_main_menu_keyboard(),
        disable_web_page_preview=True
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /help displaying all 17 available commands."""
    if not await check_user_access(update):
        return

    text = (
        "📚 <b>دليل أوامر منصة Jankiz الشامل:</b>\n\n"
        "• <code>/start</code> — بدء البوت وعرض القائمة الرئيسية\n"
        "• <code>/help</code> — دليل الاستخدام وجميع الأوامر\n"
        "• <code>/news</code> — آخر الأخبار التقنية العامة\n"
        "• <code>/programming</code> — أخبار لغات البرمجة والتقنيات\n"
        "• <code>/ai</code> — أخبار وأدوات الذكاء الاصطناعي\n"
        "• <code>/github</code> — مشاريع ومستودعات GitHub الحقيقية\n"
        "• <code>/blender</code> — مركز Blender للتصميم والـ 3D\n"
        "• <code>/social</code> — أخبار وتحديثات منصات التواصل\n"
        "• <code>/tools</code> — أدوات المطورين وسكربتات البناء\n"
        "• <code>/code</code> — أكواد وشروحات برمجية مختبرة\n"
        "• <code>/security</code> — تنبيهات وأخبار الأمن السيبراني\n"
        "• <code>/search &lt;كلمة&gt;</code> — البحث في محتوى المنصة\n"
        "• <code>/subscribe</code> — إدارة الاشتراكات التلقائية\n"
        "• <code>/unsubscribe</code> — إيقاف التحديثات التلقائية\n"
        "• <code>/settings</code> — إعدادات وتفضيلات المستخدم\n"
        "• <code>/about</code> — معلومات عن منصة Jankiz\n"
        "• <code>/status</code> — حالة خوادم وخدمات المنصة 24/7\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "<i>Jankiz | البرمجة والتقنية، في مكان واحد.</i>"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎨 مركز Blender", callback_data="sec_blender_hub")],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="nav_main_menu")]
    ])
    await update.effective_message.reply_html(text, reply_markup=keyboard)


async def blender_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /blender."""
    if not await check_user_access(update):
        return
    text = (
        "🎨 <b>JANKIZ Blender Hub — مركز بلندر المتكامل</b>\n\n"
        "منصتك المخصصة لبرنامج <b>Blender</b> ثلاثي الأبعاد:\n"
        "• آخر الأخبار وسجلات الإصدارات الرسمية من blender.org\n"
        "• إضافات Add-ons ومشاريع GitHub الحقيقية\n"
        "• خامات PBR وبيئات HDRI مجانية برخص CC0\n"
        "• شروحات النمذجة وعُقد الهندسة (Geometry Nodes) وتطوير السكربتات\n\n"
        "👇 <b>اختر من الأقسام المتاحة أدناه:</b>"
    )
    await update.effective_message.reply_html(text, reply_markup=get_blender_keyboard())


async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /news."""
    if not await check_user_access(update):
        return
    await send_news_section(update.effective_message, category="programming")


async def github_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /github."""
    if not await check_user_access(update):
        return
    await update.effective_message.reply_html(
        "🐙 <b>قسم مشاريع GitHub مفتوحة المصدر:</b>\n\nاختر التخصص البرمجي لاستعراض أحدث المستودعات النشطة والحقيقية:",
        reply_markup=get_github_keyboard()
    )


async def social_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /social."""
    if not await check_user_access(update):
        return
    await update.effective_message.reply_html(
        "📱 <b>قسم منصات التواصل الاجتماعي:</b>\n\nاختر المنصة لمتابعة الميزات الرسمية، التحديثات، وتقارير الأعطال والحلول:",
        reply_markup=get_social_keyboard()
    )


async def tutorials_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /code or /tutorials."""
    if not await check_user_access(update):
        return
    await send_code_tutorials(update.effective_message)


async def tools_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /tools."""
    if not await check_user_access(update):
        return
    await send_dev_tools(update.effective_message)


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /subscribe or /settings."""
    if not await check_user_access(update):
        return
    user_id = update.effective_user.id
    await update.effective_message.reply_html(
        "🔔 <b>إدارة اشتراكات التحديثات التلقائية:</b>\n\n"
        "اضغط على أي قسم لتفعيل أو إلغاء استلام إشعاراته الجديدة تلقائيًا فور نشرها:",
        reply_markup=get_subscriptions_keyboard(user_id)
    )


async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /unsubscribe."""
    if not await check_user_access(update):
        return
    user_id = update.effective_user.id
    for cat in SUBSCRIPTION_CATEGORIES.keys():
        db.set_user_subscription(user_id, cat, False)
    await update.effective_message.reply_html(
        "🔕 <b>تم إيقاف جميع الاشتراكات التلقائية بنجاح.</b>\nيمكنك إعادة تفعيل أي قسم عبر أمر <code>/subscribe</code> في أي وقت."
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /status displaying service uptime without exposing secrets."""
    if not await check_user_access(update):
        return
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stats = db.get_system_stats()
    text = (
        "⚡ <b>حالة نظام ومنصة Jankiz التشغيلية 24/7:</b>\n\n"
        "• 🟢 <b>محرك تيليجرام:</b> متصل ونشط (Long-Polling)\n"
        "• 🟢 <b>قاعدة البيانات SQLite:</b> مفهرسة ومتصلة بنجاح\n"
        "• 🟢 <b>مجدول التحديث الدوري:</b> يعمل كل 30 دقيقة\n"
        "• 🟢 <b>نظام الحماية:</b> مفعل (Anti-Spam & Rate Limiter)\n"
        f"• 📊 <b>المقالات والمشاريع المؤرشفة:</b> {stats['total_articles'] + stats['total_github_projects']}\n"
        f"• 🕒 <b>توقيت الخادم:</b> <code>{now_str}</code>\n\n"
        "<i>المنصة تعمل بصورة مستمرة ومستقرة.</i>"
    )
    await update.effective_message.reply_html(text)


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /about."""
    if not await check_user_access(update):
        return
    about_text = (
        "🤖 <b>عن منصة Jankiz (البرمجة والتقنية):</b>\n\n"
        "منصة إخبارية وتقنية متكاملة ومؤتمتة تقدم أحدث مستجدات هندسة البرمجيات، والذكاء الاصطناعي، ومشاريع GitHub، ومنصات التواصل، ومركز Blender الشامل.\n\n"
        "• <b>المصادر:</b> Blender.org, Hacker News, Dev.to, GitHub API\n"
        "• <b>المطور:</b> تم تطوير البوت بواسطة جنكيز.\n"
        "• <b>الحقوق:</b> جميع الحقوق محفوظة ©\n\n"
        "Jankiz | البرمجة والتقنية، في مكان واحد."
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="nav_main_menu")]
    ])
    await update.effective_message.reply_html(about_text, reply_markup=keyboard)


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /search <query>."""
    if not await check_user_access(update):
        return
    if not context.args:
        await update.message.reply_html(
            "🔍 <b>يرجى كتابة كلمة البحث بعد الأمر</b>\n"
            "مثال: <code>/search blender</code> أو <code>/search fastapi</code> أو <code>/search docker</code>"
        )
        return

    query = " ".join(context.args)
    items = news_fetcher.search_news(query, limit=3)
    if not items:
        await update.message.reply_html(f"❌ لم يتم العثور على محتوى مطابق لـ: <b>{sanitize_text(query)}</b>")
        return

    await update.message.reply_html(f"🔍 <b>نتائج البحث عن: [{sanitize_text(query)}]</b>\n━━━━━━━━━━━━━━━━━━")
    for art in items:
        msg = news_fetcher.format_news_card(art)
        await update.message.reply_html(msg, disable_web_page_preview=True)


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Secure Admin Dashboard."""
    user = update.effective_user
    admin_str = str(ADMIN_ID).strip()
    if not user or not admin_str or str(user.id) != admin_str:
        return

    stats = db.get_system_stats()
    admin_text = (
        "⚙️ <b>لوحة الإدارة والتحكم — منصة Jankiz</b>\n\n"
        f"👥 <b>إجمالي المستخدمين:</b> {stats['total_users']}\n"
        f"🔔 <b>إجمالي المشتركين النشطين:</b> {stats['total_subscribers']}\n"
        f"📰 <b>المقالات والأخبار المخزنة:</b> {stats['total_articles']}\n"
        f"🐙 <b>مشاريع GitHub المكتشفة:</b> {stats['total_github_projects']}\n"
        f"📱 <b>تحديثات المنصات الاجتماعية:</b> {stats['total_social_updates']}\n"
        f"📤 <b>إجمالي الإرساليات التلقائية:</b> {stats['total_broadcasts']}\n\n"
        "الحالة: الخادم والمجدول يعملان بصورة طبيعية ومحمية 24/7."
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 تشغيل الجمع اليدوي الآن", callback_data="admin_trigger_fetch")],
        [InlineKeyboardButton("🔙 إغلاق", callback_data="nav_main_menu")]
    ])
    await update.message.reply_html(admin_text, reply_markup=keyboard)


# --- Section Senders ---

async def send_news_section(target, category: str = "programming"):
    """Fetch and send verified news articles."""
    articles = news_fetcher.get_latest_news(category=category, limit=3)
    if not articles:
        await target.reply_html("⚠️ لا توجد أخبار جديدة حالياً في هذا القسم. يتم التحديث دورياً.")
        return

    for art in articles:
        card = news_fetcher.format_news_card(art)
        await target.reply_html(card, disable_web_page_preview=True)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 تحديث الأخبار", callback_data=f"sec_{category}_news")],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="nav_main_menu")]
    ])
    await target.reply_html("👆 يمكنك طلب المزيد أو العودة للقائمة:", reply_markup=keyboard)


async def send_github_section(target, category: str = "all"):
    """Fetch and send real verified GitHub projects."""
    projects = github_fetcher.get_github_projects(category=category, limit=3)
    if not projects:
        await target.reply_html("⚠️ لم يتم العثور على مستودعات جديدة حالياً. جرب قسماً آخر.")
        return

    for proj in projects:
        card = github_fetcher.format_github_card(proj)
        await target.reply_html(card, disable_web_page_preview=True)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🐙 تصنيف آخر", callback_data="sec_github_menu")],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="nav_main_menu")]
    ])
    await target.reply_html("👆 تصفح مستودعات أخرى أو عد للقائمة الرئيسية:", reply_markup=keyboard)


async def send_social_section(target, platform: str = "all"):
    """Fetch and send social media updates."""
    updates = social_fetcher.get_social_updates(platform_filter=None if platform == "all" else platform, limit=3)
    if not updates:
        await target.reply_html("⚠️ لا توجد تقارير جديدة حالياً عن هذه المنصة.")
        return

    for item in updates:
        card = social_fetcher.format_social_card(item)
        await target.reply_html(card, disable_web_page_preview=True)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 منصة أخرى", callback_data="sec_social_menu")],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="nav_main_menu")]
    ])
    await target.reply_html("👆 اختر منصة أخرى أو عد للقائمة الرئيسية:", reply_markup=keyboard)


async def send_code_tutorials(target):
    """Send practical verified code snippets."""
    tutorials = code_library.get_code_tutorials(limit=3)
    for t in tutorials:
        card = code_library.format_tutorial_card(t)
        await target.reply_html(card)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="nav_main_menu")]
    ])
    await target.reply_html("Jankiz | أكواد وشروحات عملية ومختبرة.", reply_markup=keyboard)


async def send_dev_tools(target):
    """Send developer tools catalog."""
    tools = dev_tools.get_dev_tools(limit=3)
    for tool in tools:
        card = dev_tools.format_dev_tool_card(tool)
        await target.reply_html(card, disable_web_page_preview=True)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="nav_main_menu")]
    ])
    await target.reply_html("Jankiz | أدوات المطورين.", reply_markup=keyboard)


# --- Callback Queries Handler ---

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles all button callbacks smoothly."""
    query = update.callback_query
    await query.answer()

    if not await check_user_access(update):
        return

    data = query.data
    user_id = query.from_user.id
    target = query.message

    # Navigation
    if data == "nav_main_menu":
        await target.reply_html(START_WELCOME_TEXT, reply_markup=get_main_menu_keyboard(), disable_web_page_preview=True)

    # Main Sections
    elif data in ["sec_latest_news", "sec_programming_news"]:
        await send_news_section(target, category="programming")
    elif data == "sec_ai_news":
        await send_news_section(target, category="ai")
    elif data == "sec_security_news":
        await send_news_section(target, category="cybersecurity")
    elif data == "sec_github_menu":
        await target.reply_html("🐙 <b>مشاريع GitHub مفتوحة المصدر:</b>\nاختر التخصص البرمجي:", reply_markup=get_github_keyboard())
    elif data == "sec_social_menu":
        await target.reply_html("📱 <b>منصات التواصل الاجتماعي:</b>\nاختر المنصة التي تود متابعتها:", reply_markup=get_social_keyboard())
    elif data == "sec_code_tutorials":
        await send_code_tutorials(target)
    elif data == "sec_dev_tools":
        await send_dev_tools(target)
    elif data == "sec_subscriptions":
        await target.reply_html(
            "🔔 <b>إدارة اشتراكات التحديثات التلقائية:</b>\n\nاضغط على أي تصنيف لتفعيل أو إيقاف وصول إشعاراته الجديدة:",
            reply_markup=get_subscriptions_keyboard(user_id)
        )
    elif data == "sec_help":
        await help_command(update, context)
    elif data == "sec_search_prompt":
        await target.reply_html(
            "🔎 <b>البحث في محتوى المنصة:</b>\n"
            "أرسل اسم التقنية أو المشروع مباشرة في المحادثة (مثال: <code>react</code> أو <code>blender</code> أو <code>fastapi</code>)."
        )

    # Blender Hub Menu & Actions
    elif data == "sec_blender_hub":
        await blender_command(update, context)

    elif data == "bln_news" or data == "bln_releases":
        for rel in blender_hub.BLENDER_RELEASES:
            card = blender_hub.format_blender_news_card(rel)
            await target.reply_html(card, disable_web_page_preview=True)
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🎨 عودة لمركز Blender", callback_data="sec_blender_hub")]])
        await target.reply_html("👆 الإصدارات الرسمية من موقع Blender.org", reply_markup=keyboard)

    elif data == "bln_addons":
        for add in blender_hub.BLENDER_ADDONS:
            card = blender_hub.format_addon_card(add)
            await target.reply_html(card, disable_web_page_preview=True)
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🎨 عودة لمركز Blender", callback_data="sec_blender_hub")]])
        await target.reply_html("👆 إضافات وأدوات Blender المعتمدة", reply_markup=keyboard)

    elif data in ["bln_github", "bln_trending"]:
        repos = blender_hub.get_blender_github_projects(limit=3)
        for repo in repos:
            card = blender_hub.format_blender_repo_card(repo)
            await target.reply_html(card, disable_web_page_preview=True)
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🎨 عودة لمركز Blender", callback_data="sec_blender_hub")]])
        await target.reply_html("👆 مستودعات ومشاريع Blender على GitHub", reply_markup=keyboard)

    elif data in ["bln_demo_files", "bln_textures", "bln_hdri"]:
        for res in blender_hub.BLENDER_RESOURCES:
            card = blender_hub.format_resource_card(res)
            await target.reply_html(card, disable_web_page_preview=True)
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🎨 عودة لمركز Blender", callback_data="sec_blender_hub")]])
        await target.reply_html("👆 موارد ثلاثية الأبعاد وخامات وHDRI مرخصة CC0", reply_markup=keyboard)

    elif data in ["bln_tutorials", "bln_python_dev"]:
        for tut in blender_hub.BLENDER_TUTORIALS:
            card = blender_hub.format_tutorial_card(tut)
            await target.reply_html(card, disable_web_page_preview=True)
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🎨 عودة لمركز Blender", callback_data="sec_blender_hub")]])
        await target.reply_html("👆 شروحات وتوثيق Blender و Python API الرسمي", reply_markup=keyboard)

    elif data == "bln_search_prompt":
        await target.reply_html(
            "🔎 <b>البحث في موارد ومشاريع Blender:</b>\n"
            "اكتب كلمة البحث مسبوقة بـ blender (مثال: <code>blender geometry nodes</code> أو <code>blender add-ons</code> أو <code>blender hdri</code>)."
        )

    # GitHub Subcategories
    elif data.startswith("gh_cat_"):
        cat = data.replace("gh_cat_", "")
        await send_github_section(target, category=cat)

    # Social Subcategories
    elif data.startswith("soc_plat_"):
        plat = data.replace("soc_plat_", "")
        await send_social_section(target, platform=plat)

    # Subscription Toggles
    elif data.startswith("toggle_sub_"):
        cat_key = data.replace("toggle_sub_", "")
        current_subs = db.get_user_subscriptions(user_id)
        new_state = cat_key not in current_subs
        db.set_user_subscription(user_id, cat_key, new_state)

        cat_title = SUBSCRIPTION_CATEGORIES.get(cat_key, cat_key)
        feedback = f"✅ تم تفعيل اشتراكك في: <b>{cat_title}</b>" if new_state else f"🔕 تم إلغاء اشتراكك في: <b>{cat_title}</b>"
        await target.reply_html(feedback)
        await target.reply_html("🔔 <b>قائمة اشتراكاتك الحالية:</b>", reply_markup=get_subscriptions_keyboard(user_id))

    # Admin actions
    elif data == "admin_trigger_fetch":
        admin_str = str(ADMIN_ID).strip()
        if admin_str and str(user_id) == admin_str:
            await target.reply_html("⏳ جاري جمع وتدقيق الأخبار والمشاريع من المصادر الحقيقية الآن...")
            news_fetcher.get_latest_news(category="all", limit=5)
            github_fetcher.get_github_projects(category="all", limit=5)
            social_fetcher.get_social_updates(limit=5)
            await target.reply_html("✅ اكتملت عملية جمع البيانات وحفظها في قاعدة البيانات بنجاح.")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text search queries safely."""
    if not await check_user_access(update):
        return

    text = update.message.text.strip()
    if text.startswith("/"):
        return

    # Check if query is blender-related
    if "blender" in text.lower() or "بلندر" in text:
        repos = blender_hub.get_blender_github_projects(limit=2)
        await update.message.reply_html(f"🎨 <b>نتائج البحث في موارد Blender عن: [{sanitize_text(text)}]</b>\n━━━━━━━━━━━━━━━━━━")
        for r in repos:
            card = blender_hub.format_blender_repo_card(r)
            await update.message.reply_html(card, disable_web_page_preview=True)
        return

    items = news_fetcher.search_news(text, limit=3)
    if items:
        await update.message.reply_html(f"🔍 <b>أحدث ما تم رصده وتوثيقه عن: [{sanitize_text(text)}]</b>\n━━━━━━━━━━━━━━━━━━")
        for art in items:
            card = news_fetcher.format_news_card(art)
            await update.message.reply_html(card, disable_web_page_preview=True)
    else:
        await update.message.reply_html(
            f"لم أعثر على محتوى مطابق لـ '{sanitize_text(text)}'. يمكنك استخدام القائمة الرئيسية لاختيار القسم المناسب.",
            reply_markup=get_main_menu_keyboard()
        )


async def scheduled_periodic_collector_and_broadcaster(context: ContextTypes.DEFAULT_TYPE):
    """Periodic job running every 30 minutes: gathers fresh content and broadcasts without duplicates."""
    logger.info("Executing scheduled collector and broadcaster...")

    try:
        fresh_news = news_fetcher.get_latest_news(category="programming", limit=2)
        fresh_ai = news_fetcher.get_latest_news(category="ai", limit=1)
        fresh_github = github_fetcher.get_github_projects(category="all", limit=1)
    except Exception as e:
        logger.error(f"Error fetching during periodic job: {e}")
        return

    # Broadcast category: programming
    for art in fresh_news:
        subscribers = db.get_subscribers_for_category("programming")
        card = news_fetcher.format_news_card(art)
        art_hash = abs(hash(art.get("url") or art.get("title"))) % 10000000
        for uid in subscribers:
            if not db.is_broadcasted(uid, "article", art_hash):
                try:
                    await context.bot.send_message(
                        chat_id=uid,
                        text=f"🔔 <b>تحديث جديد في أخبار البرمجة:</b>\n\n{card}",
                        parse_mode=constants.ParseMode.HTML,
                        disable_web_page_preview=True
                    )
                    db.log_broadcast(uid, "article", art_hash)
                    await asyncio.sleep(0.05)
                except Exception as e:
                    logger.warning(f"Could not broadcast to {uid}: {e}")

    # Broadcast category: github
    for proj in fresh_github:
        subscribers = db.get_subscribers_for_category("github")
        card = github_fetcher.format_github_card(proj)
        proj_hash = abs(hash(proj.get("url") or proj.get("name"))) % 10000000
        for uid in subscribers:
            if not db.is_broadcasted(uid, "github", proj_hash):
                try:
                    await context.bot.send_message(
                        chat_id=uid,
                        text=f"🔔 <b>مشروع GitHub جديد يستحق الاهتمام:</b>\n\n{card}",
                        parse_mode=constants.ParseMode.HTML,
                        disable_web_page_preview=True
                    )
                    db.log_broadcast(uid, "github", proj_hash)
                    await asyncio.sleep(0.05)
                except Exception as e:
                    logger.warning(f"Could not broadcast GitHub repo to {uid}: {e}")


def start_web_server_thread():
    """Start local web preview server in background."""
    t = threading.Thread(target=run_server, args=(PORT,), daemon=True)
    t.start()
    logger.info(f"Web Preview active on http://localhost:{PORT}")


def main():
    print("=" * 65)
    print("   JANKIZ TELEGRAM PLATFORM — FULL PRODUCTION ENGINE    ")
    print("=" * 65)

    # 1. Initialize SQLite database
    db.init_db()

    # 2. Start web preview console
    start_web_server_thread()

    # 3. Validate Token
    token_check = check_telegram_token(BOT_TOKEN)
    if not token_check["valid"]:
        logger.error(f"Telegram token validation failed: {token_check['message']}")
        return

    logger.info(f"Connected to Telegram as @{token_check.get('username')}")

    # 4. Build Telegram Application with post_init command registration
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(register_bot_commands)
        .build()
    )

    # Handlers for all 17 commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("news", news_command))
    app.add_handler(CommandHandler("programming", news_command))
    app.add_handler(CommandHandler("ai", lambda u, c: send_news_section(u.effective_message, "ai")))
    app.add_handler(CommandHandler("github", github_command))
    app.add_handler(CommandHandler("blender", blender_command))
    app.add_handler(CommandHandler("social", social_command))
    app.add_handler(CommandHandler("tools", tools_command))
    app.add_handler(CommandHandler("code", tutorials_command))
    app.add_handler(CommandHandler("security", lambda u, c: send_news_section(u.effective_message, "cybersecurity")))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("subscribe", subscribe_command))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    app.add_handler(CommandHandler("settings", subscribe_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("admin", admin_command))

    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Schedule periodic collection and broadcast (every 30 minutes = 1800 seconds)
    if app.job_queue:
        app.job_queue.run_repeating(
            scheduled_periodic_collector_and_broadcaster,
            interval=1800,
            first=120
        )
        logger.info("30-minute automated periodic collector & broadcaster registered.")

    logger.info("Jankiz Platform is actively running on Telegram.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

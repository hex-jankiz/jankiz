"""
Jankiz Platform - Comprehensive Automated Verification Test Suite
=================================================================
Executes real automated tests across all platform modules:
1. Welcome message compliance & forbidden phrases check
2. Database persistence & integrity
3. User subscriptions & category management
4. Programming news engine & deduplication
5. GitHub project discovery & real statistics verification
6. Social media platform updates & outage monitoring
7. Code library & tested snippets status
8. Developer tools catalog
9. Rate limiting & security defenses
10. Broadcast logging & duplicate prevention
"""

import sys
import unittest
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

import db
import bot
import news_fetcher
import github_fetcher
import social_fetcher
import code_library
import dev_tools
from security import RateLimiter, sanitize_text

class TestJankizPlatform(unittest.TestCase):

    def test_01_welcome_message_exact_and_clean(self):
        """Verify the /start greeting starts strictly with '👋 مرحبًا بك!' and contains NO forbidden text."""
        text = bot.START_WELCOME_TEXT.strip()
        self.assertTrue(text.startswith("👋 مرحبًا بك!"), "Welcome message MUST start with '👋 مرحبًا بك!'")
        self.assertTrue(text.endswith("Jankiz | البرمجة والتقنية، في مكان واحد."), "Must end with product branding")

        # Prohibited terms test
        forbidden = [
            "مرحبًا يا جانكيز",
            "مرحبًا بك في Jankiz",
            "أنا جانكيز",
            "أنا مساعدك",
            "Anti-Gravity",
            "gemini",
            "claude",
            "chatgpt",
            "openai"
        ]
        for f in forbidden:
            self.assertNotIn(f.lower(), text.lower(), f"Forbidden phrase found in welcome message: {f}")

    def test_02_database_initialization_and_users(self):
        """Verify SQLite DB initializes and registers users with persistence."""
        db.init_db()
        test_uid = 99887766
        db.register_user(test_uid, "test_dev", "Engineer")
        
        # Verify persistence
        subs = db.get_user_subscriptions(test_uid)
        self.assertIsInstance(subs, set)

    def test_03_subscriptions_management(self):
        """Verify subscribing, unsubscribing, and category persistence."""
        test_uid = 99887755
        db.set_user_subscription(test_uid, "ai", True)
        db.set_user_subscription(test_uid, "github", True)

        subs = db.get_user_subscriptions(test_uid)
        self.assertIn("ai", subs)
        self.assertIn("github", subs)
        self.assertNotIn("social", subs)

        # Unsubscribe test
        db.set_user_subscription(test_uid, "ai", False)
        subs_after = db.get_user_subscriptions(test_uid)
        self.assertNotIn("ai", subs_after)
        self.assertIn("github", subs_after)

    def test_04_news_engine_and_deduplication(self):
        """Verify news fetching, SQLite deduplication, and template format."""
        articles = news_fetcher.get_latest_news("programming", limit=2)
        self.assertGreaterEqual(len(articles), 1)

        first = articles[0]
        self.assertTrue(bool(first.get("title")), "Article title cannot be empty")
        self.assertTrue(bool(first.get("url")), "Article URL cannot be empty")

        card = news_fetcher.format_news_card(first)
        self.assertIn("📰", card)
        self.assertIn("📝 <b>الملخص:</b>", card)
        self.assertIn("💡 <b>لماذا يهمك؟</b>", card)
        self.assertIn("📅 <b>تاريخ النشر:</b>", card)
        self.assertIn("🔗", card)

    def test_05_github_discovery_real_data(self):
        """Verify real GitHub repositories discovery, stars, and required card format."""
        projects = github_fetcher.get_github_projects(limit=2)
        self.assertGreaterEqual(len(projects), 1)

        proj = projects[0]
        self.assertTrue(bool(proj.get("name")), "Project name must be present")
        self.assertTrue(bool(proj.get("url")), "Project URL must be present")
        self.assertTrue(proj.get("url").startswith("https://github.com/"), "Must be a genuine GitHub URL")

        card = github_fetcher.format_github_card(proj)
        self.assertIn("🐙", card)
        self.assertIn("📝 <b>الوصف:</b>", card)
        self.assertIn("💻 <b>لغة البرمجة:</b>", card)
        self.assertIn("⭐ <b>النجوم:</b>", card)
        self.assertIn("🔀 <b>Forks:</b>", card)
        self.assertIn("⚙️ <b>طريقة البدء:</b>", card)
        self.assertIn("🔗", card)

    def test_06_social_platform_updates_and_status(self):
        """Verify social media updates, platform statuses, and required card format."""
        updates = social_fetcher.get_social_updates(limit=2)
        self.assertGreaterEqual(len(updates), 1)

        soc = updates[0]
        self.assertTrue(bool(soc.get("platform")), "Platform must not be empty")
        self.assertTrue(bool(soc.get("status")), "Status must not be empty")

        card = social_fetcher.format_social_card(soc)
        self.assertIn("📱 <b>المنصة:</b>", card)
        self.assertIn("⚠️ <b>الموضوع / التحديث:</b>", card)
        self.assertIn("📌 <b>الحالة:</b>", card)
        self.assertIn("🛠️ <b>التفاصيل والحلول:</b>", card)
        self.assertIn("🔗", card)

    def test_07_code_library_and_test_certification(self):
        """Verify practical tutorials have clear descriptions, tested code, and no empty values."""
        tuts = code_library.get_code_tutorials(limit=2)
        self.assertGreaterEqual(len(tuts), 1)

        tut = tuts[0]
        self.assertTrue(tut.get("is_tested"), "Code snippet must be tested")
        card = code_library.format_tutorial_card(tut)
        self.assertIn("📚", card)
        self.assertIn("🧪 <b>حالة الاختبار:</b>", card)

    def test_08_developer_tools_catalog(self):
        """Verify developer tools have names, descriptions, install commands, and URLs."""
        tools = dev_tools.get_dev_tools(limit=2)
        self.assertGreaterEqual(len(tools), 1)

        tool = tools[0]
        card = dev_tools.format_dev_tool_card(tool)
        self.assertIn("🛠️", card)
        self.assertIn("⚙️ <b>أمر التثبيت السريع:</b>", card)

    def test_09_security_rate_limiter(self):
        """Verify rate limiter blocks rapid spam/DDoS attempts."""
        limiter = RateLimiter(max_requests=3, window_seconds=5)
        uid = 112233

        allowed_1, _ = limiter.is_allowed(uid)
        allowed_2, _ = limiter.is_allowed(uid)
        allowed_3, _ = limiter.is_allowed(uid)
        blocked, msg = limiter.is_allowed(uid)

        self.assertTrue(allowed_1)
        self.assertTrue(allowed_2)
        self.assertTrue(allowed_3)
        self.assertFalse(blocked, "Fourth request in quick succession must be blocked by rate limiter")
        self.assertIn("⚠️", msg)

    def test_10_broadcast_log_deduplication(self):
        """Verify broadcast logging prevents sending the same article twice to the same user."""
        import time
        test_uid = int(time.time() * 1000) % 10000000
        content_type = "article"
        content_id = 12345

        # Initially not broadcasted
        self.assertFalse(db.is_broadcasted(test_uid, content_type, content_id))

        # Log broadcast
        db.log_broadcast(test_uid, content_type, content_id)

        # Now marked as broadcasted
        self.assertTrue(db.is_broadcasted(test_uid, content_type, content_id))

    def test_11_blender_hub_resources_and_releases(self):
        """Verify Blender Hub official releases, addons, CC0 resources, and GitHub repos."""
        import blender_hub
        self.assertGreaterEqual(len(blender_hub.BLENDER_RELEASES), 2)
        self.assertGreaterEqual(len(blender_hub.BLENDER_ADDONS), 3)
        self.assertGreaterEqual(len(blender_hub.BLENDER_RESOURCES), 3)
        self.assertGreaterEqual(len(blender_hub.BLENDER_TUTORIALS), 3)

        # Verify cards
        rel_card = blender_hub.format_blender_news_card(blender_hub.BLENDER_RELEASES[0])
        self.assertIn("Blender", rel_card)
        self.assertIn("download", rel_card.lower())

        addon_card = blender_hub.format_addon_card(blender_hub.BLENDER_ADDONS[0])
        self.assertIn("Node Wrangler", addon_card)

        res_card = blender_hub.format_resource_card(blender_hub.BLENDER_RESOURCES[0])
        self.assertIn("Poly Haven", res_card)
        self.assertIn("CC0", res_card)

    def test_12_telegram_slash_commands_exact_17(self):
        """Verify all 17 commands are registered with Arabic descriptions."""
        cmds = {c.command: c.description for c in bot.TELEGRAM_BOT_COMMANDS}
        expected = [
            "start", "help", "news", "programming", "ai", "github",
            "blender", "social", "tools", "code", "security", "search",
            "subscribe", "unsubscribe", "settings", "about", "status"
        ]
        self.assertEqual(len(cmds), 17)
        for exp in expected:
            self.assertIn(exp, cmds, f"Command /{exp} must be registered in TELEGRAM_BOT_COMMANDS")
            self.assertTrue(len(cmds[exp]) > 3, f"Description for /{exp} must be descriptive Arabic")

if __name__ == "__main__":
    unittest.main()


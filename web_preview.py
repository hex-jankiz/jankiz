"""
Jankiz Platform - Web Console & Interactive Preview
===================================================
واجهة تحكم ومحاكاة ويب تفاعلية لمنصة Jankiz
"""

import sys
import os
import json
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

import news_fetcher
import github_fetcher
import social_fetcher
import code_library
import dev_tools
import db
from config import BOT_TOKEN, PORT

def check_telegram_token(token: str):
    """Check if the provided token is valid with Telegram API."""
    if not token or len(token) < 15:
        return {"valid": False, "message": "التوكن فارغ أو غير مكتمل."}
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        req = urllib.request.Request(url, headers={"User-Agent": "JankizBot/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                if data.get("ok"):
                    bot_info = data.get("result", {})
                    return {
                        "valid": True,
                        "bot_name": bot_info.get("first_name"),
                        "username": bot_info.get("username"),
                        "can_join_groups": bot_info.get("can_join_groups", False),
                        "message": f"التوكن صحيح! البوت متصل باسم @{bot_info.get('username')}"
                    }
    except Exception as e:
        return {"valid": False, "message": f"خطأ في التحقق من التوكن: {e}"}
    return {"valid": False, "message": "التوكن غير صالح أو منتهي الصلاحية (401 Unauthorized)."}

START_WELCOME_HTML = """👋 <b>مرحبًا بك!</b><br><br>
🚀 <b>منصتك لمتابعة أحدث التطورات في عالم البرمجة والذكاء الاصطناعي والتكنولوجيا.</b><br><br>
💻 <b>أخبار البرمجة</b><br>
تابع أحدث لغات البرمجة وأطر العمل والمكتبات والتحديثات التي تهم المطورين.<br><br>
🤖 <b>الذكاء الاصطناعي</b><br>
اكتشف النماذج الجديدة والأدوات الذكية والتطبيقات العملية والتطورات الحديثة.<br><br>
📱 <b>منصات التواصل الاجتماعي</b><br>
تابع تحديثات TikTok وYouTube وInstagram وFacebook وWhatsApp وTelegram وغيرها، مع أخبار الميزات الجديدة والمشكلات والحلول الموثوقة.<br><br>
🐙 <b>مشاريع GitHub</b><br>
اكتشف مشاريع مفتوحة المصدر حقيقية، وأدوات برمجية مفيدة، ومكتبات جديدة، ومشاريع تستحق التجربة والتعلم منها.<br><br>
🛠️ <b>أدوات المطورين</b><br>
تعرّف على الأدوات التي تساعدك على كتابة الكود وتحسين الأداء وبناء التطبيقات.<br><br>
🔐 <b>الأمن السيبراني</b><br>
تابع التحديثات الأمنية والتنبيهات المهمة والممارسات التي تساعد على حماية التطبيقات والأنظمة.<br><br>
📚 <b>أكواد وشروحات عملية</b><br>
استفد من أمثلة برمجية مفيدة ومشاريع قابلة للتحقق وشروحات واضحة.<br><br>
━━━━━━━━━━━━━━━━━━<br><br>
👇 <b>اختر القسم الذي يهمك من القائمة أدناه، أو اشترك في التحديثات لتصلك الأخبار الجديدة تلقائيًا.</b><br><br>
<i>Jankiz | البرمجة والتقنية، في مكان واحد.</i>"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Jankiz — البرمجة والتقنية، في مكان واحد</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --tg-blue: #2481cc;
      --tg-blue-hover: #1c6ba8;
      --bg: #0e1621;
      --surface: #17212b;
      --surface-light: #242f3d;
      --border: #2b394a;
      --text: #f5f5f5;
      --muted: #7f91a4;
      --accent: #64b5f6;
    }
    body {
      font-family: 'IBM Plex Sans Arabic', system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    .header {
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 1rem 1.5rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .brand { display: flex; align-items: center; gap: .75rem; }
    .brand__avatar {
      width: 44px; height: 44px; border-radius: 50%;
      background: linear-gradient(135deg, #2481cc, #64b5f6);
      display: flex; align-items: center; justify-content: center;
      font-size: 1.25rem; font-weight: 700; color: #fff;
    }
    .brand__details h1 { font-size: 1.15rem; font-weight: 600; }
    .brand__details p { font-size: .8rem; color: var(--muted); }
    .status-badge {
      display: flex; align-items: center; gap: .5rem;
      padding: .4rem .8rem; border-radius: 20px; font-size: .82rem;
      background: rgba(76, 175, 80, 0.15); color: #81c784;
      border: 1px solid rgba(76, 175, 80, 0.3);
    }
    .status-dot { width: 8px; height: 8px; border-radius: 50%; background: #4caf50; }

    .main-container {
      flex: 1; max-width: 900px; width: 100%;
      margin: 1.5rem auto; padding: 0 1rem;
      display: flex; flex-direction: column; gap: 1.5rem;
    }
    .chat-card {
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 16px; overflow: hidden; display: flex;
      flex-direction: column; height: 640px;
    }
    .chat-history {
      flex: 1; padding: 1.25rem; overflow-y: auto;
      display: flex; flex-direction: column; gap: 1rem;
      background: #0e1621;
    }
    .msg {
      max-width: 85%; padding: .875rem 1.125rem; border-radius: 12px;
      font-size: .925rem; line-height: 1.6;
    }
    .msg--bot {
      align-self: flex-start; background: var(--surface-light);
      border-bottom-right-radius: 4px; border: 1px solid rgba(255,255,255,0.06);
    }
    .msg--user {
      align-self: flex-end; background: var(--tg-blue); color: #fff;
      border-bottom-left-radius: 4px;
    }
    .msg pre {
      background: rgba(0,0,0,0.35); padding: .5rem; border-radius: 6px;
      margin: .5rem 0; font-family: monospace; direction: ltr; text-align: left;
      overflow-x: auto;
    }
    .msg a { color: var(--accent); text-decoration: none; font-weight: 500; }
    .msg a:hover { text-decoration: underline; }

    .quick-actions {
      background: var(--surface); border-top: 1px solid var(--border);
      padding: .75rem 1rem; display: flex; flex-wrap: wrap; gap: .5rem;
    }
    .chip {
      background: var(--surface-light); border: 1px solid var(--border);
      color: var(--text); padding: .45rem .8rem; border-radius: 20px;
      font-size: .82rem; font-family: inherit; cursor: pointer;
      display: flex; align-items: center; gap: .35rem; transition: all .18s;
    }
    .chip:hover {
      background: var(--tg-blue); border-color: var(--tg-blue); color: #fff;
    }

    .chat-input-bar {
      padding: .75rem 1rem; background: var(--surface);
      border-top: 1px solid var(--border); display: flex; gap: .75rem;
    }
    .chat-input {
      flex: 1; height: 42px; background: var(--bg); border: 1px solid var(--border);
      border-radius: 8px; padding: 0 1rem; font-family: inherit; color: #fff;
      outline: none; font-size: .9rem;
    }
    .chat-input:focus { border-color: var(--tg-blue); }
    .send-btn {
      background: var(--tg-blue); border: none; color: #fff;
      width: 44px; height: 42px; border-radius: 8px; cursor: pointer;
      display: flex; align-items: center; justify-content: center;
    }
  </style>
</head>
<body>

  <header class="header">
    <div class="brand">
      <div class="brand__avatar">J</div>
      <div class="brand__details">
        <h1>Jankiz — البرمجة والتقنية</h1>
        <p>منصة متكاملة للأخبار، والذكاء الاصطناعي، ومشاريع GitHub، ومنصات التواصل</p>
      </div>
    </div>
    <div class="status-badge">
      <span class="status-dot"></span>
      <span>المنصة نشطة وتعمل 24/7</span>
    </div>
  </header>

  <main class="main-container">
    <div class="chat-card">
      <div class="chat-history" id="chatHistory">
        <div class="msg msg--bot" id="initialMsg">
          """ + START_WELCOME_HTML + """
        </div>
      </div>

      <div class="quick-actions">
        <button class="chip" onclick="sendCommand('/news')">📰 آخر الأخبار</button>
        <button class="chip" onclick="sendCommand('/programming')">💻 أخبار البرمجة</button>
        <button class="chip" onclick="sendCommand('/ai')">🤖 الذكاء الاصطناعي</button>
        <button class="chip" onclick="sendCommand('/github')">🐙 مشاريع GitHub</button>
        <button class="chip" onclick="sendCommand('/blender')">🎨 Blender Hub</button>
        <button class="chip" onclick="sendCommand('/social')">📱 منصات التواصل</button>
        <button class="chip" onclick="sendCommand('/tools')">🛠️ أدوات المطورين</button>
        <button class="chip" onclick="sendCommand('/tutorials')">📚 الأكواد والشروحات</button>
        <button class="chip" onclick="sendCommand('/security')">🔐 الأمن السيبراني</button>
        <button class="chip" onclick="sendCommand('/subscribe')">🔔 إدارة الاشتراكات</button>
        <button class="chip" onclick="sendCommand('/start')">🏠 البداية</button>
      </div>

      <div class="chat-input-bar">
        <input class="chat-input" id="userInput" placeholder="اكتب أمراً أو كلمة للبحث (مثال: python أو react أو tiktok)..." onkeypress="if(event.key==='Enter') handleSend()">
        <button class="send-btn" onclick="handleSend()" title="إرسال">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
    </div>
  </main>

  <script>
    const chat = document.getElementById('chatHistory');
    const input = document.getElementById('userInput');

    function appendMessage(text, isUser = false) {
      const msg = document.createElement('div');
      msg.className = 'msg ' + (isUser ? 'msg--user' : 'msg--bot');
      msg.innerHTML = text.replace(/\\n/g, '<br>');
      chat.appendChild(msg);
      chat.scrollTop = chat.scrollHeight;
    }

    function sendCommand(cmd) {
      appendMessage(cmd, true);
      executeAction(cmd);
    }

    function handleSend() {
      const val = input.value.trim();
      if (!val) return;
      input.value = '';
      appendMessage(val, true);
      executeAction(val);
    }

    async function executeAction(action) {
      try {
        const res = await fetch('/api/query?action=' + encodeURIComponent(action));
        const data = await res.json();
        if (data && data.reply) {
          appendMessage(data.reply);
        } else {
          appendMessage('⚠️ لم يتم العثور على محتوى جديد.');
        }
      } catch (e) {
        appendMessage('❌ حدث خطأ أثناء جلب البيانات.');
      }
    }
  </script>
</body>
</html>
"""

class BotPreviewHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
            return

        elif path == "/health" or path == "/healthz":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "healthy",
                "service": "jankiz-telegram-bot",
                "version": "2.0.0"
            }).encode("utf-8"))
            return

        elif path == "/api/query":
            qs = urllib.parse.parse_qs(parsed.query)
            action = qs.get("action", ["/news"])[0].strip()

            reply = self.handle_action(action)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"reply": reply}, ensure_ascii=False).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        # Keep logs clean in production
        return

    def handle_action(self, action: str) -> str:
        act = action.lower()

        if act in ["/start", "بداية", "مرحبا"]:
            return START_WELCOME_HTML

        elif act in ["/news", "/programming", "أخبار البرمجة", "اخبار البرمجة"]:
            arts = news_fetcher.get_latest_news("programming", limit=2)
            return "<br><br>━━━━━━━━━━━━━━━━━━<br><br>".join([news_fetcher.format_news_card(a) for a in arts])

        elif act in ["/ai", "الذكاء الاصطناعي"]:
            arts = news_fetcher.get_latest_news("ai", limit=2)
            return "<br><br>━━━━━━━━━━━━━━━━━━<br><br>".join([news_fetcher.format_news_card(a) for a in arts])

        elif act in ["/security", "الأمن السيبراني"]:
            arts = news_fetcher.get_latest_news("cybersecurity", limit=2)
            return "<br><br>━━━━━━━━━━━━━━━━━━<br><br>".join([news_fetcher.format_news_card(a) for a in arts])

        elif act in ["/github", "مشاريع github", "github"]:
            repos = github_fetcher.get_github_projects(limit=2)
            return "<br><br>━━━━━━━━━━━━━━━━━━<br><br>".join([github_fetcher.format_github_card(r) for r in repos])

        elif act in ["/blender", "blender", "بلندر"]:
            rels = blender_hub.BLENDER_RELEASES
            addons = blender_hub.BLENDER_ADDONS[:2]
            out = ["🎨 <b>JANKIZ Blender Hub — مركز بلندر المتكامل</b><br><br>"]
            for r in rels:
                out.append(blender_hub.format_blender_news_card(r))
            for a in addons:
                out.append(blender_hub.format_addon_card(a))
            return "<br><br>━━━━━━━━━━━━━━━━━━<br><br>".join(out)

        elif act in ["/social", "منصات التواصل"]:
            updates = social_fetcher.get_social_updates(limit=2)
            return "<br><br>━━━━━━━━━━━━━━━━━━<br><br>".join([social_fetcher.format_social_card(s) for s in updates])

        elif act in ["/tools", "أدوات المطورين"]:
            tools = dev_tools.get_dev_tools(limit=2)
            return "<br><br>━━━━━━━━━━━━━━━━━━<br><br>".join([dev_tools.format_dev_tool_card(t) for t in tools])

        elif act in ["/tutorials", "الأكواد والشروحات"]:
            tuts = code_library.get_code_tutorials(limit=2)
            return "<br><br>━━━━━━━━━━━━━━━━━━<br><br>".join([code_library.format_tutorial_card(t) for t in tuts])

        elif act in ["/subscribe", "إدارة الاشتراكات"]:
            return (
                "🔔 <b>إدارة اشتراكات الإشعارات التلقائية:</b><br><br>"
                "• 💻 أخبار البرمجة (مفعلة)<br>"
                "• 🤖 الذكاء الاصطناعي (مفعلة)<br>"
                "• 🐙 مشاريع GitHub (مفعلة)<br>"
                "• 📱 منصات التواصل الاجتماعي (مفعلة)<br>"
                "• 🔐 الأمن السيبراني (مفعلة)<br><br>"
                "<i>يمكنك التحكم في التفضيلات مباشرة من داخل محادثة تيليجرام.</i>"
            )

        # Fallback to search
        res = news_fetcher.search_news(action, limit=2)
        if res:
            return "<br><br>━━━━━━━━━━━━━━━━━━<br><br>".join([news_fetcher.format_news_card(a) for a in res])
        return "لم يتم العثور على محتوى مطابق. اختر قسماً من الأزرار أعلاه."

def run_server(port=5000):
    server = HTTPServer(("0.0.0.0", port), BotPreviewHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    run_server(PORT)

"""
Jankiz Platform - Production & Cloud Deployment Verifier
========================================================
فاحص حالة نشر البوت واختبار الاتصال والتأكد من الجاهزية السحابية
"""

import sys
import os
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

# Add current directory to path
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from config import BOT_TOKEN, PORT

def test_telegram_api():
    """Verify Telegram Bot token and connection."""
    print("🔍 [1/3] فحص الاتصال بواجهة Telegram API...")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "JankizVerifier/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("ok"):
                bot = data["result"]
                print(f"   ✅ البوت متصل بنجاح: @{bot.get('username')} ({bot.get('first_name')})")
                return True, bot
    except Exception as e:
        print(f"   ❌ فشل الاتصال بتيليجرام: {e}")
        return False, None
    return False, None

def test_telegram_updates_queue():
    """Check pending updates on Telegram."""
    print("📬 [2/3] فحص طابور الرسائل والتحديثات المعلقة...")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "JankizVerifier/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("ok"):
                res = data["result"]
                pending = res.get("pending_update_count", 0)
                webhook_url = res.get("url", "")
                mode = f"Webhook ({webhook_url})" if webhook_url else "Long Polling"
                print(f"   ✅ وضع الاستقبال: {mode}")
                print(f"   ℹ️ عدد الرسائل بانتظار المعالجة: {pending}")
                return True, pending
    except Exception as e:
        print(f"   ⚠️ تعذر فحص طابور الرسائل: {e}")
    return False, 0

def test_cloud_url(url):
    """Test health check on the deployed cloud URL."""
    print(f"🌐 [3/3] فحص استجابة الرابط السحابي: {url}...")
    health_url = url.rstrip("/") + "/health"
    try:
        req = urllib.request.Request(health_url, headers={"User-Agent": "JankizKeepAlive/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status == 200:
                payload = json.loads(resp.read().decode("utf-8"))
                print(f"   ✅ الخادم السحابي يعمل بكفاءة: {payload}")
                return True
    except urllib.error.HTTPError as e:
        print(f"   ⚠️ الخادم السحابي رد بكود: {e.code}")
    except Exception as e:
        print(f"   ⏳ الخادم السحابي ما زال قيد الإقلاع أو البناء: {e}")
    return False

def main():
    print("=" * 60)
    print("   JANKIZ CLOUD DEPLOYMENT VERIFICATION SUITE   ")
    print("=" * 60)
    
    ok1, bot_info = test_telegram_api()
    ok2, pending = test_telegram_updates_queue()
    
    cloud_url = os.environ.get("CLOUD_URL", "")
    if len(sys.argv) > 1:
        cloud_url = sys.argv[1]
        
    if cloud_url:
        ok3 = test_cloud_url(cloud_url)
    else:
        print("💡 [3/3] لتجربة فحص الرابط السحابي، شغّل:")
        print("   python verify_deployment.py https://your-service.onrender.com")

    print("\n" + "=" * 60)
    if ok1:
        print("🎉 حالة البوت: جاهز ومتصل ومستعد لمعالجة الرسائل فوراً!")
    else:
        print("⚠️ يرجى التأكد من التوكن أو اتصال الإنترنت.")
    print("=" * 60)

if __name__ == "__main__":
    main()

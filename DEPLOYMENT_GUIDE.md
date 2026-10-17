# 🚀 دليل نشر بوت JANKIZ على استضافة سحابية مجانية 24/7

تم تجهيز هذا المشروع بالكامل ليعمل على مدار الساعة طوال أيام الأسبوع (24/7) دون الحاجة لإبقاء حاسوبك الشخصي قيد التشغيل، وذلك باستخدام الخطة المجانية لمنصة **Render.com** وبدون الحاجة لبطاقة بنكية.

---

## 📁 الملفات الإنتاجية المجهزة في المشروع

1. **`bot.py`**: المحرك الرئيسي للبوت الذي يحتوي على كافة الأوامر والخدمات، ويشغل بالتوازي خادم فحص الصحة HTTP على المنفذ المخصص `$PORT`.
2. **`requirements.txt`**: قائمة حزم Python الإنتاجية المحددة بدقة.
3. **`Procfile`**: أمر التشغيل لمنصات PaaS مثل Render.
4. **`Dockerfile`**: حاوية Docker القياسية في حال رغبت بنشره على أي منصة حاويات.
5. **`render.yaml`**: إعدادات Blueprint الخاصة بمنصة Render للنشر الآلي.
6. **`.gitignore`**: تأمين كامل لمنع رفع ملف `.env` أو توكن البوت أو قواعد البيانات إلى GitHub.

---

## 🛠️ خطوات النشر (3 خطوات بسيطة فقط)

### الخطوة 1: رفع المشروع إلى حسابك في GitHub

1. افتح الرابط: [https://github.com/new](https://github.com/new)
2. اكتب اسم المستودع: `jankiz-telegram-bot`
3. اختر نوع المستودع: **Private** (خاص) أو Public (المشروع محمي في كلتا الحالتين).
4. اضغط على **Create repository**.
5. قم برفع الكود بتنفيذ الأمرين التاليين (أو سأقوم بتنفيذهما لك):
   ```bash
   git remote add origin https://github.com/JANKIZEGYGFUEUFUB/jankiz-telegram-bot.git
   git push -u origin main
   ```

---

### الخطوة 2: إنشاء الخدمة المجانية على Render.com

1. ادخل إلى: [https://dashboard.render.com](https://dashboard.render.com) وسجّل دخولك بحساب **GitHub**.
2. اضغط على الزر الأزرق **New +** ثم اختر **Web Service**.
3. اختر مستودع **`jankiz-telegram-bot`** من القائمة واضغط **Connect**.
4. تأكد من الإعدادات التالية:
   - **Name**: `jankiz-telegram-bot`
   - **Language**: `Python 3`
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Instance Type**: اختر **Free** ($0 / month).
5. انزل إلى قسم **Environment Variables** وأضف:
   - **Key**: `BOT_TOKEN`
   - **Value**: التوكن الخاص ببوتك (`8875304971:AAGjqHzcDZ-8JyTVq7WGhqdmKYmccQ0JpXk`)
6. اضغط **Create Web Service**.

سيبدأ Render ببناء البوت وتشغيله خلال دقيقة إلى دقيقتين. ستظهر لك في السجلات رسالة:
`Connected to Telegram as @Jankiz_Code_Bot`
`Jankiz Platform is actively running on Telegram.`

---

### الخطوة 3: تفعيل التشغيل المستمر 24/7 مجاناً (منع النوم)

تقوم Render بإيقاف الخدمات المجانية مؤقتاً إذا لم تتلقَ زيارة HTTP لمدة 15 دقيقة. لمنع ذلك وجعل البوت يعمل 24 ساعة دون انقطاع:

1. انسخ رابط موقع البوت الذي يوفره لك Render (مثلاً: `https://jankiz-telegram-bot.onrender.com`).
2. افتح موقع [UptimeRobot.com](https://uptimerobot.com) وسجل حساباً مجانياً.
3. اضغط **Add New Monitor**:
   - **Monitor Type**: `HTTP(s)`
   - **Friendly Name**: `Jankiz KeepAlive`
   - **URL**: `https://jankiz-telegram-bot.onrender.com/health`
   - **Monitoring Interval**: كل `10 minutes`
4. اضغط **Create Monitor**.

هذا الفحص الدوري يرسل إشارة خفيفة لخادم البوت كل 10 دقائق، فيظل خادم البوت في Render مستيقظاً ويعمل على تيليجرام طوال الـ 24 ساعة مجاناً مدى الحياة!

"""
Jankiz Platform - JANKIZ Blender Hub
===================================
قسم مستقل ومتكامل يغطي:
- آخر أخبار وإصدارات Blender الرسمية من blender.org
- مشاريع Blender الحقيقية على GitHub وإضافات Add-ons
- ملفات .blend وخامات PBR وبيئات HDRI مجانية ومرخصة (CC0)
- دروس النمذجة وعُقد الهندسة وتطوير السكربتات بـ Python API (bpy)
"""

import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import db
from security import sanitize_text

# 1. الإصدارات والتحديثات الرسمية
BLENDER_RELEASES = [
    {
        "version": "Blender 4.3",
        "title": "إطلاق Blender 4.3 رسميًا: تحديث ثوري في Grease Pencil v3 ومحرك EEVEE Next",
        "status": "إصدار رسمي مستقر",
        "highlights": "إعادة كتابة Grease Pencil بلغة C++ لسرعة فائقة، تحسينات كبرى في تظليل EEVEE Next، ودعم تفرع Geometry Nodes الجديد وتكامل ألوان AgX.",
        "download_url": "https://www.blender.org/download/",
        "release_notes": "https://wiki.blender.org/wiki/Reference/Release_Notes/4.3",
        "date": "أحدث إصدار مستقر"
    },
    {
        "version": "Blender 4.2 LTS",
        "title": "Blender 4.2 LTS: إصدار الدعم طويل الأمد لمشاريع الاستوديوهات",
        "status": "مستقر مدعوم لسنتين",
        "highlights": "منصة Extensions Platform المدمجة لإدارة الإضافات مباشرة، استقرار عالي للرندر وتوافق واسع مع بطاقات الرسوميات الحديثة.",
        "download_url": "https://www.blender.org/download/lts/4-2/",
        "release_notes": "https://wiki.blender.org/wiki/Reference/Release_Notes/4.2",
        "date": "إصدار الدعم المستمر"
    }
]

# 2. الإضافات المعتمدة والشهيرة
BLENDER_ADDONS = [
    {
        "name": "Node Wrangler",
        "category": "Shading & Texturing",
        "description": "الإضافة الرسمية الأهم للتعامل السريع مع عُقد المواد وربط خرائط الـ PBR Textures باختصار Ctrl+Shift+T ومعاينة العُقد بـ Ctrl+Shift+Click.",
        "install": "مدمجة مسبقاً داخل بلندر: Preferences > Add-ons > ابحث عن Node Wrangler",
        "url": "https://docs.blender.org/manual/en/latest/addons/node/node_wrangler.html"
    },
    {
        "name": "Auto-Rig Pro",
        "category": "Rigging & Character Animation",
        "description": "أداة متقدمة لتوليد الهياكل العظمية الذكية للشخصيات وتصديرها المتوافق مباشرة مع محركات Unreal Engine و Unity.",
        "install": "تثبيت كإضافة .zip عبر Preferences > Add-ons",
        "url": "https://blendermarket.com/products/auto-rig-pro"
    },
    {
        "name": "BlenderGIS",
        "category": "Geo-Data & 3D Environments",
        "description": "إضافة مفتوحة المصدر لاستيراد خرائط الارتفاعات (DEM) ونماذج المدن والمباني ثلاثية الأبعاد وبيانات OpenStreetMap في بلندر.",
        "install": "تثبيت كإضافة من مستودع GitHub الرسمي",
        "url": "https://github.com/domlysz/BlenderGIS"
    },
    {
        "name": "Screencast Keys",
        "category": "UI & Tutorial Tools",
        "description": "أداة عرض أزرار لوحة المفاتيح ونقرات الفأرة مباشرة على شاشة العرض، مثالية لصناع المحتوى والمدربين.",
        "install": "تثبيت كإضافة zip عبر Preferences",
        "url": "https://github.com/nutti/Screencast-Keys"
    }
]

# 3. الموارد المجانية ومرخصة CC0 (خامات، بيئات، ملفات .blend)
BLENDER_RESOURCES = [
    {
        "type": "HDRI & Environments",
        "name": "Poly Haven (مكتبة بيئات الإضاءة و HDRI)",
        "license": "CC0 (ملكية عامة مجانية 100% للأعمال الشخصية والتجارية)",
        "description": "آلاف بيئات الإضاءة الواقعية بدقة فائقة تصل إلى 16K بصيغ EXR و HDR جاهزة للرندر الواقعي في Cycles و EEVEE.",
        "url": "https://polyhaven.com/hdris"
    },
    {
        "type": "PBR Textures & Materials",
        "name": "AmbientCG (خامات ومواد احترافية PBR)",
        "license": "CC0 Public Domain",
        "description": "أكثر من 2000 مادة خام مع خرائط Normal و Roughness و Displacement و Ambient Occlusion جاهزة للسحب والإفلات.",
        "url": "https://ambientcg.com"
    },
    {
        "type": "Official .blend Demo Files",
        "name": "ملفات مشاريع أفلام Blender Studio الرسمية",
        "license": "Creative Commons / Blender Open Projects",
        "description": "مشاهد كاملة لاختبار الرندر والأفلام القصيرة الرسمية (مثل Sprite Fright و Charge و Cosmos Laundromat) لتفكيك الإضاءة والتحريك.",
        "url": "https://www.blender.org/download/demo-files/"
    }
]

# 4. الدروس والشروحات المعتمدة
BLENDER_TUTORIALS = [
    {
        "title": "سلسلة أساسيات Blender الرسمية للمبتدئين",
        "topic": "الواجهة والنمذجة والإضاءة",
        "level": "مبتدئ",
        "source": "Blender Foundation Official",
        "url": "https://www.blender.org/support/tutorials/"
    },
    {
        "title": "دليل إتقان Geometry Nodes والتوليد الإجرائي",
        "topic": "العُقد الهندسية والمؤثرات الإجرائية",
        "level": "متوسط إلى متقدم",
        "source": "Blender Documentation",
        "url": "https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/index.html"
    },
    {
        "title": "برمجة السكربتات وتطوير الإضافات بـ Python API (bpy)",
        "topic": "أتمتة المهام وبناء أدوات مخصصة",
        "level": "مطورين",
        "source": "Blender Python API Docs",
        "url": "https://docs.blender.org/api/current/"
    }
]

def get_blender_github_projects(limit: int = 3) -> List[Dict[str, Any]]:
    """Retrieve real Blender repositories from GitHub."""
    results = []
    try:
        url = "https://github.com/topics/blender"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            articles = soup.find_all("article", class_="border")
            for art in articles[:limit]:
                h3 = art.find("h3")
                if not h3 or not h3.find_all("a"):
                    continue
                links = h3.find_all("a")
                owner = links[0].text.strip()
                repo = links[1].text.strip()
                repo_url = f"https://github.com/{owner}/{repo}"
                desc_p = art.find("p")
                desc = desc_p.text.strip() if desc_p else "مستودع مفتوح المصدر مرتبط بـ Blender"

                stars_a = art.find("a", href=lambda h: h and h.endswith("/stargazers"))
                stars = stars_a.text.strip() if stars_a else "N/A"

                results.append({
                    "name": repo,
                    "owner": owner,
                    "description": desc,
                    "stars": stars,
                    "url": repo_url,
                    "language": "Python / C++",
                    "license": "GPL / MIT"
                })
    except Exception as e:
        print(f"[BlenderHub] GitHub fetch fallback: {e}")

    if not results:
        results = [
            {
                "name": "blender",
                "owner": "blender",
                "description": "The official Blender source code repository. Open source 3D creation pipeline.",
                "stars": "13,000+",
                "url": "https://github.com/blender/blender",
                "language": "C / C++ / Python",
                "license": "GPL-3.0"
            },
            {
                "name": "BlenderGIS",
                "owner": "domlysz",
                "description": "Blender addons to import geographic GIS data (shapefiles, satellite imagery, DEM).",
                "stars": "7,800+",
                "url": "https://github.com/domlysz/BlenderGIS",
                "language": "Python",
                "license": "GPL-3.0"
            }
        ]
    return results[:limit]

# --- بطاقات العرض المصممة بعناية ---

def format_blender_news_card(item: Dict[str, Any]) -> str:
    title = sanitize_text(item.get("title", ""))
    ver = sanitize_text(item.get("version", ""))
    stat = sanitize_text(item.get("status", "رسمي"))
    high = sanitize_text(item.get("highlights", ""))
    d_url = item.get("download_url", "https://www.blender.org")
    notes = item.get("release_notes", "https://www.blender.org")
    date = sanitize_text(item.get("date", "محدث"))

    return (
        f"🎨 <b>[{ver}] {title}</b>\n\n"
        f"📌 <b>الحالة:</b> {stat} | 📅 <b>التاريخ:</b> {date}\n\n"
        f"✨ <b>أهم الميزات والتحديثات:</b>\n{high}\n\n"
        f"📥 <a href='{d_url}'>تنزيل الإصدار الرسمي ↗</a>\n"
        f"📄 <a href='{notes}'>سجل التغييرات الكامل (Release Notes) ↗</a>"
    )

def format_addon_card(addon: Dict[str, Any]) -> str:
    name = sanitize_text(addon.get("name", ""))
    cat = sanitize_text(addon.get("category", ""))
    desc = sanitize_text(addon.get("description", ""))
    inst = sanitize_text(addon.get("install", ""))
    url = addon.get("url", "https://blender.org")

    return (
        f"🧩 <b>إضافة: {name}</b>\n"
        f"🏷️ <b>التصنيف:</b> {cat}\n\n"
        f"📝 <b>الوظيفة:</b>\n{desc}\n\n"
        f"⚙️ <b>طريقة التثبيت:</b>\n<code>{inst}</code>\n\n"
        f"🔗 <a href='{url}'>المصدر والتوثيق الرسمي ↗</a>"
    )

def format_resource_card(res: Dict[str, Any]) -> str:
    typ = sanitize_text(res.get("type", "مورد ثلاثي الأبعاد"))
    name = sanitize_text(res.get("name", ""))
    lic = sanitize_text(res.get("license", "CC0"))
    desc = sanitize_text(res.get("description", ""))
    url = res.get("url", "#")

    return (
        f"📦 <b>{name}</b>\n"
        f"🏷️ <b>النوع:</b> {typ} | ⚖️ <b>الترخيص:</b> {lic}\n\n"
        f"📝 <b>الوصف:</b>\n{desc}\n\n"
        f"🔗 <a href='{url}'>زيارة مكتبة الموارد وتنزيل الملفات ↗</a>"
    )

def format_tutorial_card(tut: Dict[str, Any]) -> str:
    title = sanitize_text(tut.get("title", ""))
    topic = sanitize_text(tut.get("topic", ""))
    lvl = sanitize_text(tut.get("level", "عام"))
    src = sanitize_text(tut.get("source", "توثيق رسمي"))
    url = tut.get("url", "https://blender.org")

    return (
        f"🎬 <b>{title}</b>\n\n"
        f"🎯 <b>الموضوع:</b> {topic} | 📊 <b>المستوى:</b> {lvl}\n"
        f"🌐 <b>المصدر:</b> {src}\n\n"
        f"🔗 <a href='{url}'>الانتقال إلى الشرح والتطبيق ↗</a>"
    )

def format_blender_repo_card(repo: Dict[str, Any]) -> str:
    name = sanitize_text(repo.get("name", ""))
    owner = sanitize_text(repo.get("owner", ""))
    desc = sanitize_text(repo.get("description", ""))
    stars = sanitize_text(str(repo.get("stars", "N/A")))
    lang = sanitize_text(repo.get("language", "Python"))
    url = repo.get("url", "https://github.com")

    return (
        f"🧑‍💻 <b>مستودع: {name}</b> ({owner})\n\n"
        f"📝 <b>الوصف:</b> {desc}\n\n"
        f"⭐ <b>النجوم:</b> {stars} | 💻 <b>اللغة:</b> {lang}\n\n"
        f"🔗 <a href='{url}'>المستودع الأصلي على GitHub ↗</a>"
    )

"""
🤖 בוט וואטסאפ משולב – מריק + חיה
גרסה 4 – עם זיכרון קבוע + מודול אימונים
"""

import os
import json
import logging
from flask import Flask, request
from anthropic import Anthropic
from datetime import datetime

# ─────────────────────────────────────────────
# ⚙️ הגדרות
# ─────────────────────────────────────────────
ANTHROPIC_API_KEY   = os.environ.get("ANTHROPIC_API_KEY", "")
MARIK_PHONE         = "whatsapp:+972526451400"
HAYA_PHONE          = "whatsapp:+972586655430"
DAILY_CALORIE_LIMIT = 2000
DATA_FILE           = "/tmp/bot_data.json"
# ─────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)

# ══════════════════════════════════════════════
# 💾 שמירת זיכרון בקובץ
# ══════════════════════════════════════════════

def load_data() -> dict:
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_data(data: dict):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Save error: {e}")

def get_user(phone: str, bot_type: str) -> tuple:
    all_data = load_data()
    today = datetime.now().strftime("%d/%m/%Y")
    if phone not in all_data:
        all_data[phone] = {
            "bot": bot_type, "history": [],
            "meals": [], "total_calories": 0,
            "exercise": False, "exercise_log": [], "date": today
        }
    elif all_data[phone].get("date") != today:
        all_data[phone].update({
            "meals": [], "total_calories": 0,
            "exercise": False, "exercise_log": [], "date": today
        })
    return all_data, all_data[phone]

# ══════════════════════════════════════════════
# 🥗 בוט התזונה – מריק
# ══════════════════════════════════════════════

DIET_SYSTEM = f"""אתה מאמן בריאות אישי חם ומקצועי, המתמחה בתזונה ים-תיכונית, הפחתת כולסטרול, אורח חיים פעיל ואימוני כושר.

המסגרת האישית של מריק:
- מסגרת קלורית יומית: {DAILY_CALORIE_LIMIT} קלוריות
- פעילות גופנית נדרשת: לפחות 30 דקות ביום
- תזונה: ים-תיכונית, דלת-פחמימות, דלת-כולסטרול
- רמת כושר: בינונית
- מקומות אימון: בית (ללא ציוד), חדר כושר, בחוץ

משימות:
1. מעקב קלורי – הערך קלוריות, ספר כמה נותרו, התריע אם חרג
2. מעקב כולסטרול – עדיף דגים/קטניות/ירקות, הזהר מבשר אדום/מטוגן/שמנת
3. מעקב פעילות – אשר, עודד, תזכר
4. סיכום יומי ("סיכום") – קלוריות, פעילות, ציון + עידוד
5. תוכנית אימון – כשמבקשים "אימון" תן תוכנית מפורטת:
   - ציין מיקום (בית/חדר כושר/חוץ)
   - חימום 5 דקות
   - 4-5 תרגילים עם סטים וחזרות
   - קירור 5 דקות
   - משך כולל: 30-45 דקות
   - מותאם לרמה בינונית

פקודות אימון:
- "אימון בית" ← תוכנית לבית ללא ציוד
- "אימון חדר כושר" ← תוכנית לחדר כושר
- "אימון חוץ" ← ריצה/הליכה + תרגילים
- "אימון היום" ← תוכנית מגוונת לפי יום בשבוע

תמיד בעברית, קצר וברור. אל תאבחן מבחינה רפואית."""

DIET_WELCOME = f"""שלום! 👋 אני הבוט הבריאותי שלך.

🎯 *המסגרת היומית:*
🔥 {DAILY_CALORIE_LIMIT} קלוריות
🏃 30 דקות פעילות ביום
❤️ תזונה דלת-כולסטרול

📋 רישום ארוחה ← כתוב מה אכלת
🏃 פעילות ← "התאמנתי + מה עשית"
💪 אימון ← "אימון בית" / "אימון חדר כושר" / "אימון חוץ"
📊 סיכום יום ← "סיכום"
🍽️ המלצה ← "הצע ארוחה"
💡 טיפ ← "טיפ"
🏆 ← "עודד אותי"

בוא נתחיל! מה אכלת היום? 🥗"""

# ══════════════════════════════════════════════
# ✍️ בוט הכתיבה – חיה (מוזה)
# ══════════════════════════════════════════════

WRITING_SYSTEM = """אתה "מוזה" – מנהל פרויקט כתיבה מקצועי ומסודר של חיה, כותבת שעובדת בלחץ של דד-ליין.

סגנון: מקצועי, ממוקד, ישיר. תגובות קצרות (וואטסאפ). חם אבל לא סנטימנטלי. אמוג'י בצמצום.

1. יעדי כתיבה יומיים – עקוב, חשב פערים, דווח בצורה ברורה
2. ניהול דד-ליין – חשב ימים שנשארו → מילים שנשארו → יעד יומי
3. חסם כתיבה – פרומפט ממוקד, שאלה על דמות/פרק, תרגיל "כתיבה חופשית ל-10 דקות"
4. הרגעה – הכר במצב (משפט אחד) → תרגיל נשימה (שאפי 4, החזיקי 4, נשפי 4) → חזרה לעבודה

כשמדווחים על יעד:
"📋 לוח עבודה:
• X ימים לדד-ליין
• נשאר: X מילים
• יעד יומי: X מילים"

כשמדווחים על התקדמות:
"✓ X מילים | יעד: X | [עמדת / נשאר X עוד]"

תמיד בעברית. תגובות קצרות – זה וואטסאפ לא מייל."""

WRITING_WELCOME = """שלום חיה! ✍️ אני מוזה – מנהל הפרויקט של הספר שלך.

מה אני יכול לעשות?
📋 לוח זמנים ← שלחי: "דד-ליין [תאריך], [X] מילים בסה"כ, כתבתי [X]"
✓ דיווח ← "כתבתי X מילים היום"
🔒 תקיעות ← "אני תקועה"
😤 לחץ ← "אני מוצפת"
📊 סיכום ← "מה המצב?"

נתחיל – ספרי לי על הפרויקט שלך 📖"""

# ══════════════════════════════════════════════
# 🔧 פונקציות צ'אט
# ══════════════════════════════════════════════

def estimate_calories(msg: str) -> int:
    msg = msg.lower()
    if any(w in msg for w in ["סלט", "ירק", "מרק"]): return 200
    if any(w in msg for w in ["פסטה", "אורז", "לחם", "פיתה"]): return 450
    if any(w in msg for w in ["בשר", "שניצל", "המבורגר"]): return 600
    if any(w in msg for w in ["דג", "טונה", "סלמון"]): return 350
    if any(w in msg for w in ["קפה", "תה", "שתיתי"]): return 50
    return 350

def chat_diet(phone: str, message: str) -> str:
    all_data, u = get_user(phone, "diet")
    remaining = DAILY_CALORIE_LIMIT - u["total_calories"]
    context = (
        f"היום: {u['date']} ({datetime.now().strftime('%A')})\n"
        f"קלוריות: {u['total_calories']}/{DAILY_CALORIE_LIMIT} (נותרו: {remaining})\n"
        f"פעילות: {'✅' if u['exercise'] else '❌ עדיין לא'}\n"
    )
    if u["meals"]:
        context += "ארוחות:\n" + "\n".join(f"- {m}" for m in u["meals"])

    history = u["history"][-20:]
    response = anthropic.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=DIET_SYSTEM + f"\n\nמצב נוכחי:\n{context}",
        messages=history + [{"role": "user", "content": message}],
    )
    reply = response.content[0].text

    u["history"] = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": reply}
    ]

    if any(t in message for t in ["אכלתי", "שתיתי", "לארוחת", "לבוקר", "לצהריים", "לערב", "לנשנוש"]):
        u["meals"].append(f"[{datetime.now().strftime('%H:%M')}] {message}")
        u["total_calories"] += estimate_calories(message)

    if any(t in message for t in ["התאמנתי", "הלכתי", "רצתי", "כושר", "יוגה", "הליכה", "ריצה", "אימון"]):
        u["exercise"] = True
        u["exercise_log"].append(f"[{datetime.now().strftime('%H:%M')}] {message}")

    save_data(all_data)
    return reply

def chat_writing(phone: str, message: str) -> str:
    all_data, u = get_user(phone, "writing")
    history = u["history"][-20:]

    response = anthropic.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=WRITING_SYSTEM,
        messages=history + [{"role": "user", "content": message}],
    )
    reply = response.content[0].text

    u["history"] = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": reply}
    ]

    save_data(all_data)
    return reply

def make_twiml(text: str) -> str:
    safe = (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{safe}</Message></Response>'

# ══════════════════════════════════════════════
# 🌐 Webhook
# ══════════════════════════════════════════════

@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    message     = (request.values.get("Body") or "").strip()
    from_number = request.values.get("From") or ""

    if not message:
        return make_twiml("לא קיבלתי הודעה 🙂"), 200, {"Content-Type": "text/xml"}

    if message == "נקה":
        all_data = load_data()
        today = datetime.now().strftime("%d/%m/%Y")
        if from_number in all_data:
            bot = all_data[from_number].get("bot", "diet")
            all_data[from_number] = {
                "bot": bot, "history": [],
                "meals": [], "total_calories": 0,
                "exercise": False, "exercise_log": [], "date": today
            }
            save_data(all_data)
        return make_twiml("✅ נמחק. התחלה חדשה!"), 200, {"Content-Type": "text/xml"}

    try:
        all_data = load_data()
        is_new = from_number not in all_data
        is_greeting = message.lower() in ["שלום", "היי", "הי", "start"]

        if from_number == HAYA_PHONE:
            reply = WRITING_WELCOME if (is_new and is_greeting) else chat_writing(from_number, message)
        else:
            reply = DIET_WELCOME if (is_new and is_greeting) else chat_diet(from_number, message)

        return make_twiml(reply), 200, {"Content-Type": "text/xml"}

    except Exception as e:
        logging.error(f"Error: {e}")
        return make_twiml("אירעה שגיאה, נסה שוב 🙏"), 200, {"Content-Type": "text/xml"}

@app.route("/", methods=["GET"])
def health():
    return "🤖 הבוט המשולב פעיל!", 200

if __name__ == "__main__":
    app.run(debug=False, port=5000)

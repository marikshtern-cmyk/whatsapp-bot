"""
🤖 בוט וואטסאפ משולב – מריק + חיה
בוט תזונה למריק | בוט כתיבה (מוזה) לחיה
webhook אחד – שני בוטים לפי מספר טלפון

התקנה: pip install flask anthropic twilio
הפעלה:  python combined_bot.py
"""

from flask import Flask, request
from anthropic import Anthropic
from datetime import datetime
import logging

# ─────────────────────────────────────────────
# 🔑 הכנס את המפתח שלך כאן
# ─────────────────────────────────────────────
ANTHROPIC_API_KEY = "YOUR_ANTHROPIC_API_KEY"
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
# 📱 מספרי הטלפון – הכנס את המספרים האמיתיים
# פורמט: "whatsapp:+972XXXXXXXXX"
# ─────────────────────────────────────────────
MARIK_PHONE  = "whatsapp:+972XXXXXXXXX"   # המספר של מריק
HAYA_PHONE   = "whatsapp:+972XXXXXXXXX"   # המספר של חיה
# ─────────────────────────────────────────────

DAILY_CALORIE_LIMIT = 1800

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)

# אחסון זיכרון
user_data: dict = {}

# ══════════════════════════════════════════════
# 🥗 בוט התזונה – מריק
# ══════════════════════════════════════════════

DIET_SYSTEM = f"""אתה מאמן בריאות אישי חם ומקצועי, המתמחה בתזונה ים-תיכונית, הפחתת כולסטרול ואורח חיים פעיל.

המסגרת האישית:
- מסגרת קלורית יומית: {DAILY_CALORIE_LIMIT} קלוריות
- פעילות גופנית נדרשת: לפחות 30 דקות ביום
- תזונה: ים-תיכונית, דלת-פחמימות, דלת-כולסטרול

1. מעקב קלורי – הערך קלוריות, ספר כמה נותרו, התריע אם חרג
2. מעקב כולסטרול – עדיף דגים/קטניות/ירקות, הזהר מבשר אדום/מטוגן/שמנת
3. מעקב פעילות גופנית – אשר, עודד, תזכר
4. סיכום יומי ("סיכום") – קלוריות, פעילות, ציון + עידוד

תמיד בעברית, קצר וחם. אל תאבחן מבחינה רפואית."""

DIET_WELCOME = f"""שלום! 👋 אני הבוט הבריאותי שלך.

🎯 *המסגרת היומית:*
🔥 {DAILY_CALORIE_LIMIT} קלוריות
🏃 30 דקות פעילות ביום
❤️ תזונה דלת-כולסטרול

📋 רישום ארוחה ← כתוב מה אכלת
🏃 פעילות ← "התאמנתי + מה עשית"
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
# 🔧 פונקציות עזר
# ══════════════════════════════════════════════

def get_user(phone: str, bot_type: str) -> dict:
    today = datetime.now().strftime("%d/%m/%Y")
    if phone not in user_data:
        user_data[phone] = {
            "bot": bot_type, "history": [],
            "meals": [], "total_calories": 0,
            "exercise": False, "exercise_log": [], "date": today
        }
    elif user_data[phone].get("date") != today:
        user_data[phone].update({
            "meals": [], "total_calories": 0,
            "exercise": False, "exercise_log": [], "date": today
        })
    return user_data[phone]


def estimate_calories(msg: str) -> int:
    msg = msg.lower()
    if any(w in msg for w in ["סלט", "ירק", "מרק"]): return 200
    if any(w in msg for w in ["פסטה", "אורז", "לחם", "פיתה"]): return 450
    if any(w in msg for w in ["בשר", "שניצל", "המבורגר"]): return 600
    if any(w in msg for w in ["דג", "טונה", "סלמון"]): return 350
    if any(w in msg for w in ["קפה", "תה", "שתיתי"]): return 50
    return 350


def build_diet_context(phone: str) -> str:
    u = get_user(phone, "diet")
    remaining = DAILY_CALORIE_LIMIT - u["total_calories"]
    ctx  = f"היום: {u['date']}\n"
    ctx += f"קלוריות: {u['total_calories']}/{DAILY_CALORIE_LIMIT} (נותרו: {remaining})\n"
    ctx += f"פעילות: {'✅' if u['exercise'] else '❌ עדיין לא'}\n"
    if u["meals"]:
        ctx += "ארוחות:\n" + "\n".join(f"- {m}" for m in u["meals"])
    return ctx


def chat_diet(phone: str, message: str) -> str:
    u = get_user(phone, "diet")
    context = build_diet_context(phone)
    history = u["history"][-20:]

    response = anthropic.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=DIET_SYSTEM + f"\n\nמצב נוכחי:\n{context}",
        messages=history + [{"role": "user", "content": message}],
    )
    reply = response.content[0].text
    u["history"].extend([{"role": "user", "content": message}, {"role": "assistant", "content": reply}])

    # רישום ארוחה אוטומטי
    if any(t in message for t in ["אכלתי", "שתיתי", "לארוחת", "לבוקר", "לצהריים", "לערב", "לנשנוש"]):
        u["meals"].append(f"[{datetime.now().strftime('%H:%M')}] {message}")
        u["total_calories"] += estimate_calories(message)

    # רישום פעילות אוטומטי
    if any(t in message for t in ["התאמנתי", "הלכתי", "רצתי", "כושר", "יוגה", "הליכה", "ריצה"]):
        u["exercise"] = True
        u["exercise_log"].append(f"[{datetime.now().strftime('%H:%M')}] {message}")

    return reply


def chat_writing(phone: str, message: str) -> str:
    u = get_user(phone, "writing")
    history = u["history"][-20:]

    response = anthropic.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=WRITING_SYSTEM,
        messages=history + [{"role": "user", "content": message}],
    )
    reply = response.content[0].text
    u["history"].extend([{"role": "user", "content": message}, {"role": "assistant", "content": reply}])
    return reply


def make_twiml(text: str) -> str:
    """עוטף תשובה בפורמט TwiML של Twilio"""
    safe = (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{safe}</Message></Response>'


# ══════════════════════════════════════════════
# 🌐 Webhook
# ══════════════════════════════════════════════

@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    message = (request.values.get("Body") or "").strip()
    from_number = request.values.get("From") or ""

    if not message:
        return make_twiml("לא קיבלתי הודעה 🙂"), 200, {"Content-Type": "text/xml"}

    # ── ניקוי ──
    if message == "נקה":
        today = datetime.now().strftime("%d/%m/%Y")
        if from_number in user_data:
            bot = user_data[from_number].get("bot", "diet")
            user_data[from_number] = {
                "bot": bot, "history": [],
                "meals": [], "total_calories": 0,
                "exercise": False, "exercise_log": [], "date": today
            }
        return make_twiml("✅ נמחק. התחלה חדשה!"), 200, {"Content-Type": "text/xml"}

    try:
        # ── ניתוב לפי מספר טלפון ──
        if from_number == HAYA_PHONE:
            # בוט הכתיבה – חיה
            if message.lower() in ["שלום", "היי", "הי", "start"] and from_number not in user_data:
                reply = WRITING_WELCOME
            else:
                reply = chat_writing(from_number, message)
        else:
            # בוט התזונה – מריק (וכל אחד אחר)
            if message.lower() in ["שלום", "היי", "הי", "start"] and from_number not in user_data:
                reply = DIET_WELCOME
            else:
                reply = chat_diet(from_number, message)

        return make_twiml(reply), 200, {"Content-Type": "text/xml"}

    except Exception as e:
        logging.error(f"Error: {e}")
        return make_twiml("אירעה שגיאה, נסה שוב 🙏"), 200, {"Content-Type": "text/xml"}


@app.route("/", methods=["GET"])
def health():
    return "🤖 הבוט המשולב פעיל!", 200


if __name__ == "__main__":
    app.run(debug=False, port=5000)


# ═══════════════════════════════════════════════════════
# 📖 הוראות הפעלה
# ═══════════════════════════════════════════════════════
#
# 1. מלא את ANTHROPIC_API_KEY
# 2. מלא את MARIK_PHONE ו-HAYA_PHONE בפורמט:
#    "whatsapp:+972501234567"
#    (לגלות את המספר – שלח הודעה לבוט, תראה את המספר ב-Twilio Logs)
# 3. הפעל:   python combined_bot.py
# 4. הפעל:   ngrok http 5000
# 5. ב-Twilio Sandbox → When a message comes in:
#    https://XXXXX.ngrok-free.dev/whatsapp
#
# ⚠️ שים לב: עצור את הבוט הישן לפני הפעלת זה!
# ═══════════════════════════════════════════════════════

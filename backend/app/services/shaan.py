from app.config import GEMINI_API_KEY, GEMINI_MODEL
from app.services.intent import predict_intent
from app.services.campus import context_for

RULES = ("You are SHAAN, the CampusVerse campus assistant. Be concise and warm. Use supplied records for campus facts. "
"Never invent attendance percentages, exam dates, rooms, deadlines, or policies. If records are missing, say so.")

def fallback(intent, ctx):
    records = ctx["records"]
    if intent == "event":
        return "Events in connected campus records:\n" + "\n".join(f"• {r['title']} — {r['event_date']} | {r['venue']}: {r['description']}" for r in records) if records else "No events are currently listed in connected records. Please check the official noticeboard."
    if intent == "notice":
        return "Latest connected notices:\n" + "\n".join(f"• {r['title']} ({r['published_on']}): {r['body']}" for r in records) if records else "No notices were found in connected records."
    if records: return "Connected campus information:\n" + "\n".join("• " + r["answer"] for r in records)
    if intent in ("attendance","exam","timetable","assignment"):
        return "Is request ke liye verified personal academic data abhi connected nahi hai, isliye main attendance, date, timetable ya deadline guess nahi karunga."
    if intent == "placement": return "Official placement dates aur eligibility abhi connected records mein nahi hain. Placement cell ke latest notices check karo."
    return "Hey! Main SHAAN hoon. Main campus events, notices aur connected campus information mein help kar sakta hoon."

def generate(prompt):
    if not GEMINI_API_KEY: return None
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        result = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        return (result.text or "").strip() or None
    except Exception:
        return None

def answer(message, role="student", department="", semester=None):
    intent, confidence = predict_intent(message)
    ctx = context_for(intent)
    prompt = f"{RULES}\nIntent: {intent}\nUser context: role={role}, department={department}, semester={semester}\nVerified records: {ctx}\nQuestion: {message}"
    response = generate(prompt) or fallback(intent, ctx)
    return {"assistant":"SHAAN","intent":intent,"confidence":round(confidence,3),"response":response,"source":ctx["source"]}

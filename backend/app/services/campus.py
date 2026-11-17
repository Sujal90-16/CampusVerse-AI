from app.db import connect

def list_rows(table, order):
    with connect() as db:
        return [dict(r) for r in db.execute(f"SELECT * FROM {table} ORDER BY {order} LIMIT 20").fetchall()]

def context_for(intent):
    if intent == "event": return {"source":"campus_events", "records":list_rows("events","event_date")}
    if intent == "notice": return {"source":"campus_notices", "records":list_rows("notices","published_on DESC")}
    if intent in ("facilities","policy","placement"):
        with connect() as db:
            rows = db.execute("SELECT category,answer,verified FROM campus_facts WHERE category=?",(intent,)).fetchall()
        return {"source":"campus_facts","records":[dict(r) for r in rows]}
    return {"source":"none","records":[]}

def events(): return list_rows("events","event_date")
def notices(): return list_rows("notices","published_on DESC")

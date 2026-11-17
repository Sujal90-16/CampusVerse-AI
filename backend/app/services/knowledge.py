import re
from app.db import connect

def chunks(text, size=700, overlap=100):
    text=re.sub(r"\s+"," ",text).strip(); out=[]; start=0
    while start<len(text):
        end=min(len(text),start+size); out.append(text[start:end])
        if end==len(text): break
        start=max(end-overlap,start+1)
    return out

def retrieve(query, limit=4):
    with connect() as db: rows=db.execute("SELECT id,title,content FROM documents").fetchall()
    if not rows:return []
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        corpus=[]; meta=[]
        for r in rows:
            for c in chunks(r["content"]): corpus.append(c); meta.append({"document_id":r["id"],"title":r["title"],"text":c})
        mat=TfidfVectorizer(ngram_range=(1,2),stop_words="english").fit_transform(corpus+[query])
        sims=cosine_similarity(mat[-1],mat[:-1]).ravel(); ranked=sims.argsort()[::-1]
        return [{**meta[i],"score":round(float(sims[i]),3)} for i in ranked[:limit] if sims[i]>0.04]
    except ValueError:return []

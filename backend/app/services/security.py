import base64, hashlib, hmac, os, time
import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import JWT_SECRET, JWT_EXPIRE_MINUTES
from app.db import connect

def hash_password(password:str)->str:
    salt=os.urandom(16); digest=hashlib.scrypt(password.encode(),salt=salt,n=2**14,r=8,p=1)
    return base64.b64encode(salt).decode()+"$"+base64.b64encode(digest).decode()

def verify_password(password:str, stored:str)->bool:
    try:
        salt_s,digest_s=stored.split("$",1); salt=base64.b64decode(salt_s); expected=base64.b64decode(digest_s)
        actual=hashlib.scrypt(password.encode(),salt=salt,n=2**14,r=8,p=1)
        return hmac.compare_digest(actual,expected)
    except Exception: return False

def create_token(user):
    now=int(time.time()); return jwt.encode({"sub":str(user["id"]),"role":user["role"],"iat":now,"exp":now+JWT_EXPIRE_MINUTES*60},JWT_SECRET,algorithm="HS256")

bearer=HTTPBearer(auto_error=False)
def current_user(credentials:HTTPAuthorizationCredentials|None=Depends(bearer)):
    if not credentials: raise HTTPException(401,"Sign in to access this resource")
    try: data=jwt.decode(credentials.credentials,JWT_SECRET,algorithms=["HS256"]); uid=int(data["sub"])
    except Exception: raise HTTPException(401,"Session is invalid or expired")
    with connect() as db: user=db.execute("SELECT id,name,email,role,department,semester,active FROM users WHERE id=?",(uid,)).fetchone()
    if not user or not user["active"]: raise HTTPException(401,"Account is unavailable")
    return dict(user)

def require_roles(*roles):
    def dependency(user=Depends(current_user)):
        if user["role"] not in roles: raise HTTPException(403,"You do not have permission to perform this action")
        return user
    return dependency

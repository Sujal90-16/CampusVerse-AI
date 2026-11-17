from contextlib import asynccontextmanager
from datetime import date, datetime
from pathlib import Path
import re, secrets
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr, field_validator
from app.db import init_db, connect
from app.config import UPLOAD_DIR, JWT_SECRET
from app.services.campus import events, notices
from app.services.shaan import answer
from app.services.security import hash_password, verify_password, create_token, current_user, require_roles
from app.services.knowledge import retrieve

@asynccontextmanager
async def lifespan(app):
    init_db(); yield
app=FastAPI(title="CampusVerse API",description="CampusVerse campus platform and SHAAN AI",version="1.0.0",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in __import__('os').getenv('CORS_ORIGINS','http://localhost:5173,http://127.0.0.1:5173').split(',')],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

class Register(BaseModel):
 name:str=Field(min_length=2,max_length=100); email:EmailStr; password:str=Field(min_length=10,max_length=128); department:str=Field(default="CSE",max_length=80); semester:int|None=Field(default=None,ge=1,le=12)
class Login(BaseModel): email:EmailStr; password:str=Field(min_length=1,max_length=128)
class ChatRequest(BaseModel): message:str=Field(min_length=1,max_length=2000); session_id:str|None=Field(default=None,max_length=100)
class CourseIn(BaseModel): code:str=Field(min_length=2,max_length=20); title:str=Field(min_length=2,max_length=120); department:str="CSE"; semester:int=Field(default=1,ge=1,le=12)
class AttendanceIn(BaseModel): student_id:int; course_id:int; class_date:date; status:str=Field(pattern='^(present|absent|late)$')
class AssignmentIn(BaseModel): title:str=Field(min_length=2,max_length=160); description:str=""; course_id:int|None=None; due_date:date|None=None
class ExamIn(BaseModel): title:str=Field(min_length=2,max_length=160); course_id:int|None=None; exam_date:date; venue:str="TBA"; department:str="CSE"; semester:int=Field(default=1,ge=1,le=12)
class NoticeIn(BaseModel): title:str=Field(min_length=2,max_length=160); category:str="General"; body:str=Field(min_length=2,max_length=5000)
class EventIn(BaseModel): title:str=Field(min_length=2,max_length=160); category:str="Campus"; event_date:date; venue:str="TBA"; description:str=""
class SubmissionIn(BaseModel): content:str=Field(min_length=1,max_length=12000)

def audit(db,user,action,entity=None,eid=None): db.execute("INSERT INTO audit_log(user_id,action,entity,entity_id) VALUES(?,?,?,?)",(user.get('id') if user else None,action,entity,eid))
def user_payload(u): return {"id":u["id"],"name":u["name"],"email":u["email"],"role":u["role"],"department":u["department"],"semester":u["semester"]}
def rowlist(sql,args=()):
 with connect() as db:return [dict(r) for r in db.execute(sql,args).fetchall()]

@app.get('/api/health')
def health(): return {"status":"ok","app":"CampusVerse","assistant":"SHAAN","version":"1.0.0"}
@app.get('/api/dashboard')
def dashboard():
 ev,no=events(),notices()
 return {"welcome":"Your campus, in sync.","stats":[{"label":"Campus events","value":f"{len(ev):02d}","note":"in connected records"},{"label":"Latest notices","value":f"{len(no):02d}","note":"in connected records"},{"label":"AI assistant","value":"Online","note":"SHAAN is ready"}],"events":ev[:3],"notices":no[:3]}
@app.get('/api/campus/events')
def get_events():return {"items":events()}
@app.get('/api/campus/notices')
def get_notices():return {"items":notices()}

@app.post('/api/auth/register',status_code=201)
def register(payload:Register):
 with connect() as db:
  if db.execute('SELECT 1 FROM users WHERE email=?',(payload.email.lower(),)).fetchone(): raise HTTPException(409,'An account with this email already exists')
  cur=db.execute('INSERT INTO users(name,email,password_hash,role,department,semester) VALUES(?,?,?,?,?,?)',(payload.name.strip(),payload.email.lower(),hash_password(payload.password),'student',payload.department,payload.semester)); uid=cur.lastrowid
  u=db.execute('SELECT id,name,email,role,department,semester FROM users WHERE id=?',(uid,)).fetchone(); audit(db,dict(u),'register','user',uid)
 return {"access_token":create_token(u),"token_type":"bearer","user":user_payload(u)}
@app.post('/api/auth/login')
def login(payload:Login):
 with connect() as db:u=db.execute('SELECT * FROM users WHERE email=?',(payload.email.lower(),)).fetchone()
 if not u or not verify_password(payload.password,u['password_hash']) or not u['active']:raise HTTPException(401,'Email or password is incorrect')
 return {"access_token":create_token(u),"token_type":"bearer","user":user_payload(u)}
@app.get('/api/auth/me')
def me(user=Depends(current_user)):return {"user":user}

@app.get('/api/academics/courses')
def courses(user=Depends(current_user)):
 if user['role'] in ('admin','faculty'): return {"items":rowlist('SELECT c.*,u.name AS faculty_name FROM courses c LEFT JOIN users u ON u.id=c.faculty_id ORDER BY c.semester,c.code')}
 return {"items":rowlist('SELECT c.* FROM courses c LEFT JOIN enrollments e ON e.course_id=c.id AND e.student_id=? WHERE e.student_id IS NOT NULL OR (c.department=? AND c.semester=?) ORDER BY c.code',(user['id'],user['department'],user['semester'] or 1))}
@app.post('/api/academics/courses',status_code=201)
def create_course(p:CourseIn,user=Depends(require_roles('admin','faculty'))):
 with connect() as db:
  cur=db.execute('INSERT INTO courses(code,title,department,semester,faculty_id) VALUES(?,?,?,?,?)',(p.code,p.title,p.department,p.semester,user['id'] if user['role']=='faculty' else None)); audit(db,user,'create','course',cur.lastrowid); return {"id":cur.lastrowid,"message":"Course created"}
@app.get('/api/academics/attendance')
def attendance(user=Depends(current_user),student_id:int|None=None):
 target=student_id if user['role'] in ('admin','faculty') and student_id else user['id']
 if user['role']=='student' and student_id and student_id!=user['id']:raise HTTPException(403,'Students can only view their own attendance')
 return {"items":rowlist("SELECT c.id AS course_id,c.code,c.title,COUNT(a.id) AS total,SUM(CASE WHEN a.status IN ('present','late') THEN 1 ELSE 0 END) AS attended,ROUND(100.0*SUM(CASE WHEN a.status IN ('present','late') THEN 1 ELSE 0 END)/NULLIF(COUNT(a.id),0),1) AS percentage FROM courses c LEFT JOIN attendance a ON a.course_id=c.id AND a.student_id=? GROUP BY c.id ORDER BY c.code",(target,))}
@app.post('/api/academics/attendance',status_code=201)
def mark_attendance(p:AttendanceIn,user=Depends(require_roles('admin','faculty'))):
 with connect() as db:
  cur=db.execute('INSERT INTO attendance(student_id,course_id,class_date,status,marked_by) VALUES(?,?,?,?,?)',(p.student_id,p.course_id,p.class_date.isoformat(),p.status,user['id'])); audit(db,user,'mark_attendance','attendance',cur.lastrowid); return {"id":cur.lastrowid,"message":"Attendance recorded"}
@app.get('/api/academics/timetable')
def timetable(user=Depends(current_user),day:str|None=None):
 sql="SELECT t.*,c.code,c.title FROM timetable t LEFT JOIN courses c ON c.id=t.course_id WHERE (t.department=? OR ? IN ('admin','faculty')) AND (t.semester=? OR ? IN ('admin','faculty'))"; args=[user['department'],user['role'],user['semester'] or 1,user['role']]
 if day:sql+=' AND lower(t.day_of_week)=lower(?)';args.append(day)
 sql+=" ORDER BY CASE t.day_of_week WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3 WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6 ELSE 7 END,t.start_time"
 return {"items":rowlist(sql,args)}
@app.get('/api/academics/assignments')
def assignments(user=Depends(current_user)):
 if user['role'] in ('admin','faculty'):
  rows=rowlist('SELECT a.*,c.code,c.title AS course_title,s.submitted_at,s.grade,s.feedback FROM assignments a LEFT JOIN courses c ON c.id=a.course_id LEFT JOIN submissions s ON s.assignment_id=a.id ORDER BY a.due_date')
 else:
  rows=rowlist('SELECT a.*,c.code,c.title AS course_title,s.submitted_at,s.grade,s.feedback FROM assignments a LEFT JOIN courses c ON c.id=a.course_id LEFT JOIN submissions s ON s.assignment_id=a.id AND s.student_id=? WHERE c.department=? AND c.semester=? ORDER BY a.due_date',(user['id'],user['department'],user['semester'] or 1))
 return {"items":rows}
@app.post('/api/academics/assignments',status_code=201)
def create_assignment(p:AssignmentIn,user=Depends(require_roles('admin','faculty'))):
 with connect() as db:
  cur=db.execute('INSERT INTO assignments(title,description,course_id,due_date,created_by) VALUES(?,?,?,?,?)',(p.title,p.description,p.course_id,p.due_date.isoformat() if p.due_date else None,user['id']));audit(db,user,'create','assignment',cur.lastrowid);return {"id":cur.lastrowid,"message":"Assignment created"}
@app.post('/api/academics/assignments/{assignment_id}/submit',status_code=201)
def submit_assignment(assignment_id:int,p:SubmissionIn,user=Depends(current_user)):
 if user['role']!='student':raise HTTPException(403,'Only students can submit assignments')
 with connect() as db:
  assignment=db.execute('SELECT a.id,c.department,c.semester FROM assignments a LEFT JOIN courses c ON c.id=a.course_id WHERE a.id=?',(assignment_id,)).fetchone()
  if not assignment:raise HTTPException(404,'Assignment not found')
  if assignment['department']!=user['department'] or assignment['semester']!=(user['semester'] or 1):raise HTTPException(403,'This assignment is not assigned to your cohort')
  db.execute('INSERT INTO submissions(assignment_id,student_id,content) VALUES(?,?,?) ON CONFLICT(assignment_id,student_id) DO UPDATE SET content=excluded.content,submitted_at=CURRENT_TIMESTAMP',(assignment_id,user['id'],p.content));audit(db,user,'submit','assignment',assignment_id)
 return {"message":"Submission saved"}
@app.get('/api/academics/exams')
def exams(user=Depends(current_user)):return {"items":rowlist("SELECT * FROM exams WHERE (department=? AND semester=?) OR ? IN ('admin','faculty') ORDER BY exam_date",(user['department'],user['semester'] or 1,user['role']))}
@app.post('/api/academics/exams',status_code=201)
def create_exam(p:ExamIn,user=Depends(require_roles('admin','faculty'))):
 with connect() as db:
  cur=db.execute('INSERT INTO exams(title,course_id,exam_date,venue,department,semester) VALUES(?,?,?,?,?,?)',(p.title,p.course_id,p.exam_date.isoformat(),p.venue,p.department,p.semester));audit(db,user,'create','exam',cur.lastrowid);return {"id":cur.lastrowid,"message":"Exam created"}

@app.post('/api/campus/notices',status_code=201)
def create_notice(p:NoticeIn,user=Depends(require_roles('admin','faculty'))):
 with connect() as db:
  cur=db.execute('INSERT INTO notices(title,published_on,category,body) VALUES(?,?,?,?)',(p.title,date.today().isoformat(),p.category,p.body));audit(db,user,'create','notice',cur.lastrowid);return {"id":cur.lastrowid,"message":"Notice published"}
@app.post('/api/campus/events',status_code=201)
def create_event(p:EventIn,user=Depends(require_roles('admin','faculty'))):
 with connect() as db:
  cur=db.execute('INSERT INTO events(title,category,event_date,venue,description) VALUES(?,?,?,?,?)',(p.title,p.category,p.event_date.isoformat(),p.venue,p.description));audit(db,user,'create','event',cur.lastrowid);return {"id":cur.lastrowid,"message":"Event published"}
@app.get('/api/admin/users')
def list_users(user=Depends(require_roles('admin'))):return {"items":rowlist('SELECT id,name,email,role,department,semester,active,created_at FROM users ORDER BY created_at DESC')}
@app.patch('/api/admin/users/{uid}/role')
def change_role(uid:int,role:str=Query(...,pattern='^(student|faculty|admin)$'),user=Depends(require_roles('admin'))):
 with connect() as db:
  if not db.execute('SELECT 1 FROM users WHERE id=?',(uid,)).fetchone():raise HTTPException(404,'User not found')
  db.execute('UPDATE users SET role=? WHERE id=?',(role,uid));audit(db,user,'change_role','user',uid)
 return {"message":"Role updated"}
@app.get('/api/admin/audit')
def audit_log(limit:int=Query(100,ge=1,le=500),user=Depends(require_roles('admin'))):return {"items":rowlist('SELECT a.*,u.name AS user_name FROM audit_log a LEFT JOIN users u ON u.id=a.user_id ORDER BY a.id DESC LIMIT ?',(limit,))}

@app.post('/api/documents/upload',status_code=201)
async def upload_document(file:UploadFile=File(...),user=Depends(require_roles('admin','faculty'))):
 name=(file.filename or 'document').lower()
 if not name.endswith(('.txt','.md','.pdf')):raise HTTPException(415,'Upload a PDF, TXT or Markdown document')
 data=await file.read(8_000_001)
 if len(data)>8_000_000:raise HTTPException(413,'Maximum upload size is 8 MB')
 try:
  if name.endswith('.pdf'):
   from pypdf import PdfReader
   import io
   content='\n'.join(page.extract_text() or '' for page in PdfReader(io.BytesIO(data)).pages)
  else:content=data.decode('utf-8')
 except Exception as exc:raise HTTPException(400,f'Could not extract document text: {exc}')
 if not content.strip():raise HTTPException(400,'No searchable text found in the document')
 with connect() as db:
  cur=db.execute('INSERT INTO documents(title,filename,content,uploaded_by) VALUES(?,?,?,?)',(Path(file.filename or 'document').stem[:160],file.filename,content,user['id']));audit(db,user,'upload','document',cur.lastrowid)
 return {"id":cur.lastrowid,"title":Path(file.filename or 'document').stem,"characters":len(content),"message":"Document indexed for SHAAN retrieval"}
@app.get('/api/documents')
def documents(user=Depends(require_roles('admin','faculty'))):return {"items":rowlist('SELECT id,title,filename,created_at FROM documents ORDER BY id DESC')}
@app.delete('/api/documents/{doc_id}')
def delete_document(doc_id:int,user=Depends(require_roles('admin'))):
 with connect() as db:
  cur=db.execute('DELETE FROM documents WHERE id=?',(doc_id,))
  if not cur.rowcount:raise HTTPException(404,'Document not found')
  audit(db,user,'delete','document',doc_id)
 return {"message":"Document deleted"}

@app.post('/api/shaan/chat')
def chat(payload:ChatRequest,user=Depends(current_user)):
 session=payload.session_id or secrets.token_urlsafe(18)
 with connect() as db:
  db.execute('INSERT INTO conversations(user_id,session_id,role,content) VALUES(?,?,?,?)',(user['id'],session,'user',payload.message))
  history=[dict(r) for r in db.execute('SELECT role,content FROM conversations WHERE user_id=? AND session_id=? ORDER BY id DESC LIMIT 8',(user['id'],session)).fetchall()]
 ctx_docs=retrieve(payload.message)
 result=answer(payload.message,user['role'],user['department'],user['semester'])
 # For academic intents, prefer authorized records over generic language-model guesses.
 intent=result.get('intent')
 q=payload.message.lower()
 if intent=='attendance':
  rows=rowlist("SELECT c.code,c.title,COUNT(a.id) AS total,SUM(CASE WHEN a.status IN ('present','late') THEN 1 ELSE 0 END) AS attended,ROUND(100.0*SUM(CASE WHEN a.status IN ('present','late') THEN 1 ELSE 0 END)/NULLIF(COUNT(a.id),0),1) AS percentage FROM courses c LEFT JOIN attendance a ON a.course_id=c.id AND a.student_id=? WHERE c.department=? AND c.semester=? GROUP BY c.id ORDER BY c.code",(user['id'],user['department'],user['semester'] or 1))
  if rows and any(r['total'] for r in rows):
   result['response']='Your connected attendance records:\n'+'\n'.join(f"• {r['code']} — {r['percentage']}% ({r['attended'] or 0}/{r['total']})" for r in rows if r['total'])
  else: result['response']='Abhi tumhare account ke liye verified attendance entries available nahi hain. Faculty ke attendance records connect hone ke baad main percentage dikha sakta hoon.'
  result['source']='authenticated academic records'
 elif intent=='timetable':
  rows=rowlist("SELECT t.day_of_week,t.start_time,t.end_time,t.room,c.code,c.title FROM timetable t LEFT JOIN courses c ON c.id=t.course_id WHERE t.department=? AND t.semester=? ORDER BY CASE t.day_of_week WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3 WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6 ELSE 7 END,t.start_time",(user['department'],user['semester'] or 1))
  if rows: result['response']='Your connected timetable (sample records may be present):\n'+'\n'.join(f"• {r['day_of_week']} {r['start_time']}–{r['end_time']} — {r['code']} {r['title']} · {r['room']}" for r in rows)
  else: result['response']='Tumhare department/semester ka timetable connected records mein nahi mila.'
  result['source']='academic timetable records'
 elif intent=='assignment':
  rows=rowlist("SELECT a.title,a.due_date,c.code FROM assignments a LEFT JOIN courses c ON c.id=a.course_id WHERE c.department=? AND c.semester=? ORDER BY a.due_date",(user['department'],user['semester'] or 1))
  result['response']='Connected assignments:\n'+'\n'.join(f"• {r['title']} ({r['code'] or 'Course TBA'}) — due {r['due_date'] or 'date not set'}" for r in rows) if rows else 'Tumhare course ke liye assignments abhi connected nahi hain.'
  result['source']='academic assignment records'
 elif intent=='exam':
  rows=rowlist("SELECT title,exam_date,venue FROM exams WHERE department=? AND semester=? ORDER BY exam_date",(user['department'],user['semester'] or 1))
  result['response']='Connected exam schedule:\n'+'\n'.join(f"• {r['title']} — {r['exam_date']} · {r['venue']}" for r in rows) if rows else 'Tumhare semester ke exams ka verified schedule connected nahi hai.'
  result['source']='academic examination records'
 if ctx_docs and result.get('intent') in ('policy','general','notice'):
  result['response'] += '\n\nFrom uploaded documents:\n'+'\n'.join(f"• {d['title']}: {d['text'][:500]}" for d in ctx_docs[:3]);result['source']='campus records + uploaded documents';result['documents']=[{"title":d['title'],"score":d['score']} for d in ctx_docs[:3]]
 with connect() as db:db.execute('INSERT INTO conversations(user_id,session_id,role,content) VALUES(?,?,?,?)',(user['id'],session,'assistant',result['response']))
 result['session_id']=session;result['history_count']=len(history);return result
@app.get('/api/shaan/history/{session_id}')
def chat_history(session_id:str,user=Depends(current_user)):
 return {"items":rowlist('SELECT role,content,created_at FROM conversations WHERE user_id=? AND session_id=? ORDER BY id',(user['id'],session_id))}

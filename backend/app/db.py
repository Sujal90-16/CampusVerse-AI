import sqlite3
from pathlib import Path
from app.config import DATABASE_PATH

def connect():
    Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
    db=sqlite3.connect(DATABASE_PATH, timeout=15)
    db.row_factory=sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    return db

def init_db():
    with connect() as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,category TEXT DEFAULT 'Campus',event_date TEXT NOT NULL,venue TEXT DEFAULT '',description TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS notices(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,published_on TEXT NOT NULL,category TEXT DEFAULT 'General',body TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS campus_facts(id INTEGER PRIMARY KEY AUTOINCREMENT,category TEXT,answer TEXT,verified INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL,role TEXT NOT NULL DEFAULT 'student',department TEXT DEFAULT '',semester INTEGER,created_at TEXT DEFAULT CURRENT_TIMESTAMP,active INTEGER DEFAULT 1);
        CREATE TABLE IF NOT EXISTS courses(id INTEGER PRIMARY KEY AUTOINCREMENT,code TEXT NOT NULL,title TEXT NOT NULL,department TEXT DEFAULT '',semester INTEGER DEFAULT 1,faculty_id INTEGER REFERENCES users(id));
        CREATE TABLE IF NOT EXISTS enrollments(id INTEGER PRIMARY KEY AUTOINCREMENT,student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,UNIQUE(student_id,course_id));
        CREATE TABLE IF NOT EXISTS attendance(id INTEGER PRIMARY KEY AUTOINCREMENT,student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,class_date TEXT NOT NULL,status TEXT NOT NULL CHECK(status IN ('present','absent','late')),marked_by INTEGER REFERENCES users(id));
        CREATE TABLE IF NOT EXISTS timetable(id INTEGER PRIMARY KEY AUTOINCREMENT,course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,day_of_week TEXT NOT NULL,start_time TEXT NOT NULL,end_time TEXT NOT NULL,room TEXT DEFAULT 'TBA',department TEXT DEFAULT '',semester INTEGER DEFAULT 1);
        CREATE TABLE IF NOT EXISTS assignments(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,description TEXT DEFAULT '',course_id INTEGER REFERENCES courses(id) ON DELETE SET NULL,due_date TEXT,created_by INTEGER REFERENCES users(id),created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS submissions(id INTEGER PRIMARY KEY AUTOINCREMENT,assignment_id INTEGER NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,content TEXT DEFAULT '',submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,grade TEXT,feedback TEXT,UNIQUE(assignment_id,student_id));
        CREATE TABLE IF NOT EXISTS exams(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,course_id INTEGER REFERENCES courses(id) ON DELETE SET NULL,exam_date TEXT NOT NULL,venue TEXT DEFAULT 'TBA',department TEXT DEFAULT '',semester INTEGER DEFAULT 1);
        CREATE TABLE IF NOT EXISTS conversations(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,session_id TEXT NOT NULL,role TEXT NOT NULL,content TEXT NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS documents(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,filename TEXT NOT NULL,content TEXT NOT NULL,uploaded_by INTEGER REFERENCES users(id),created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS audit_log(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER REFERENCES users(id),action TEXT NOT NULL,entity TEXT,entity_id INTEGER,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS colleges(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,slug TEXT NOT NULL UNIQUE,active INTEGER NOT NULL DEFAULT 1,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS subscriptions(id INTEGER PRIMARY KEY AUTOINCREMENT,college_id INTEGER NOT NULL REFERENCES colleges(id) ON DELETE CASCADE,plan TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'trial',starts_on TEXT,ends_on TEXT,seat_limit INTEGER DEFAULT 100,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS departments(id INTEGER PRIMARY KEY AUTOINCREMENT,college_id INTEGER REFERENCES colleges(id) ON DELETE CASCADE,name TEXT NOT NULL,code TEXT NOT NULL,hod_id INTEGER REFERENCES users(id),UNIQUE(college_id,code));
        CREATE TABLE IF NOT EXISTS fee_invoices(id INTEGER PRIMARY KEY AUTOINCREMENT,student_id INTEGER NOT NULL REFERENCES users(id),invoice_no TEXT NOT NULL UNIQUE,description TEXT NOT NULL,amount_paise INTEGER NOT NULL CHECK(amount_paise>=0),due_date TEXT,status TEXT NOT NULL DEFAULT 'unpaid',created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS fee_payments(id INTEGER PRIMARY KEY AUTOINCREMENT,invoice_id INTEGER NOT NULL REFERENCES fee_invoices(id),amount_paise INTEGER NOT NULL CHECK(amount_paise>0),provider_reference TEXT UNIQUE,recorded_by INTEGER REFERENCES users(id),paid_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS library_books(id INTEGER PRIMARY KEY AUTOINCREMENT,isbn TEXT,title TEXT NOT NULL,author TEXT,publisher TEXT,category TEXT,copies_total INTEGER NOT NULL DEFAULT 1 CHECK(copies_total>=0),copies_available INTEGER NOT NULL DEFAULT 1 CHECK(copies_available>=0));
        CREATE TABLE IF NOT EXISTS library_loans(id INTEGER PRIMARY KEY AUTOINCREMENT,book_id INTEGER NOT NULL REFERENCES library_books(id),student_id INTEGER NOT NULL REFERENCES users(id),issued_at TEXT DEFAULT CURRENT_TIMESTAMP,due_date TEXT NOT NULL,returned_at TEXT,status TEXT NOT NULL DEFAULT 'issued');
        CREATE TABLE IF NOT EXISTS placement_companies(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,website TEXT,industry TEXT);
        CREATE TABLE IF NOT EXISTS placement_drives(id INTEGER PRIMARY KEY AUTOINCREMENT,company_id INTEGER NOT NULL REFERENCES placement_companies(id),title TEXT NOT NULL,drive_date TEXT,eligible_department TEXT,minimum_cgpa REAL,description TEXT,status TEXT DEFAULT 'draft');
        CREATE TABLE IF NOT EXISTS placement_applications(id INTEGER PRIMARY KEY AUTOINCREMENT,drive_id INTEGER NOT NULL REFERENCES placement_drives(id),student_id INTEGER NOT NULL REFERENCES users(id),status TEXT DEFAULT 'applied',applied_at TEXT DEFAULT CURRENT_TIMESTAMP,UNIQUE(drive_id,student_id));
        CREATE TABLE IF NOT EXISTS faculty_profiles(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL UNIQUE REFERENCES users(id),employee_code TEXT UNIQUE,designation TEXT,joining_date TEXT,workload_hours REAL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS faculty_leave_requests(id INTEGER PRIMARY KEY AUTOINCREMENT,faculty_id INTEGER NOT NULL REFERENCES users(id),starts_on TEXT NOT NULL,ends_on TEXT NOT NULL,reason TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'pending',reviewed_by INTEGER REFERENCES users(id),created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS exam_seating(id INTEGER PRIMARY KEY AUTOINCREMENT,exam_id INTEGER NOT NULL REFERENCES exams(id) ON DELETE CASCADE,student_id INTEGER NOT NULL REFERENCES users(id),venue TEXT NOT NULL,seat_label TEXT NOT NULL,UNIQUE(exam_id,student_id),UNIQUE(exam_id,venue,seat_label));
        CREATE TABLE IF NOT EXISTS exam_results(id INTEGER PRIMARY KEY AUTOINCREMENT,exam_id INTEGER NOT NULL REFERENCES exams(id) ON DELETE CASCADE,student_id INTEGER NOT NULL REFERENCES users(id),marks REAL,maximum_marks REAL NOT NULL CHECK(maximum_marks>0),grade TEXT,status TEXT NOT NULL DEFAULT 'draft',entered_by INTEGER REFERENCES users(id),published_at TEXT,UNIQUE(exam_id,student_id));
        CREATE TABLE IF NOT EXISTS system_settings(key TEXT PRIMARY KEY,value TEXT NOT NULL,updated_by INTEGER REFERENCES users(id),updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS system_events(id INTEGER PRIMARY KEY AUTOINCREMENT,category TEXT NOT NULL,message TEXT NOT NULL,severity TEXT NOT NULL DEFAULT 'info',created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance(student_id,course_id);
        CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id,created_at);
        ''')
        if db.execute("SELECT COUNT(*) FROM events").fetchone()[0]==0:
            db.executemany("INSERT INTO events(title,category,event_date,venue,description) VALUES(?,?,?,?,?)",[("Campus Open Mic","Culture","2026-11-04","Student Activity Centre","An evening for music, poetry, and stand-up."),("Inter-Department Football","Sports","2026-11-08","Main Sports Ground","Team registration details will be announced by the sports office."),("Career Readiness Lab","Placement","2026-11-12","Seminar Hall 2","A practical session on resumes and interviews.")])
        if db.execute("SELECT COUNT(*) FROM notices").fetchone()[0]==0:
            db.executemany("INSERT INTO notices(title,published_on,category,body) VALUES(?,?,?,?)",[("Library hours update","2026-10-18","Facilities","Check with the library desk for confirmed opening hours."),("Placement profile checklist","2026-10-16","Placement","Keep your resume, contact details, and project links up to date.")])
        if db.execute("SELECT COUNT(*) FROM campus_facts").fetchone()[0]==0:
            db.executemany("INSERT INTO campus_facts(category,answer,verified) VALUES(?,?,?)",[("facilities","The library is in the central academic block. Confirm current opening hours with the library desk.",0),("policy","Attendance requirements vary by institution and course. Check the latest official academic regulations.",0),("placement","For official placement schedules and eligibility, consult the placement office notices.",0)])
        # Seed illustrative academic records, explicitly demo-only.
        if db.execute("SELECT COUNT(*) FROM courses").fetchone()[0]==0:
            db.executemany("INSERT INTO courses(code,title,department,semester) VALUES(?,?,?,?)",[("CSE701","Cloud Computing","CSE",7),("CSE702","Machine Learning","CSE",7),("CSE703","Professional Communication","CSE",7)])
        if db.execute("SELECT COUNT(*) FROM timetable").fetchone()[0]==0:
            db.executemany("INSERT INTO timetable(course_id,day_of_week,start_time,end_time,room,department,semester) VALUES(?,?,?,?,?,?,?)",[(1,"Monday","09:00","10:00","A-204","CSE",7),(2,"Tuesday","10:00","11:00","Lab-3","CSE",7),(3,"Wednesday","11:00","12:00","B-105","CSE",7)])
        if db.execute("SELECT COUNT(*) FROM assignments").fetchone()[0]==0:
            db.executemany("INSERT INTO assignments(title,description,course_id,due_date) VALUES(?,?,?,?)",[("Cloud architecture worksheet","Compare IaaS, PaaS and SaaS with examples.",1,"2026-10-28"),("ML model evaluation","Report precision, recall and F1 score.",2,"2026-10-30"),("Communication case study","Analyse a communication barrier scenario.",3,"2026-11-02")])
        if db.execute("SELECT COUNT(*) FROM exams").fetchone()[0]==0:
            db.executemany("INSERT INTO exams(title,course_id,exam_date,venue,department,semester) VALUES(?,?,?,?,?,?)",[("Cloud Computing internal assessment",1,"2026-11-05","Room TBA","CSE",7),("Machine Learning internal assessment",2,"2026-11-10","Room TBA","CSE",7)])

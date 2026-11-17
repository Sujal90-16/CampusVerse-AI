# CampusVerse + SHAAN AI

A campus portal starter with React, FastAPI, SQLite, JWT authentication, role-based APIs, a locally trained intent classifier, academic workflows, and document-grounded retrieval.

> **Demo data warning:** events, notices, courses, timetable, exams and assignments seeded by the app are sample records, not official institutional data.

## Stack
- React + Vite + Lucide + custom responsive CSS
- FastAPI + Pydantic REST API
- SQLite local database
- scrypt password hashing + signed JWTs
- TF-IDF + Logistic Regression intent model
- PDF/TXT/MD extraction + TF-IDF document retrieval
- Optional Gemini generation (requires your own API key)

## One-command local startup (Windows PowerShell)

For Windows, run `start-local.ps1` from the project root. It creates the backend virtual environment and installs requirements if missing, ensures `frontend/.env` points to the local API, starts the backend and frontend in separate PowerShell windows, checks the API health endpoint, and opens the browser. Keep both service windows open while using the app.

If PowerShell blocks the script, run from the project root: `powershell -ExecutionPolicy Bypass -File .\start-local.ps1`.

## Run locally (Windows PowerShell)
1. Install Python 3.11+ and Node.js 20+.
2. Copy `backend/.env.example` to `backend/.env`. Set a long unique `JWT_SECRET`. Gemini is optional.
3. Backend terminal:
   ```powershell
   cd backend
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python -m app.ml.train
   python -m app.ml.evaluate
   uvicorn app.main:app --reload --port 8000
   ```
4. Second terminal:
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```
5. Open `http://localhost:5173`; API docs: `http://127.0.0.1:8000/docs`.

## API groups
- Authentication: `/api/auth/register`, `/api/auth/login`, `/api/auth/me`
- Dashboard and campus: `/api/dashboard`, `/api/campus/events`, `/api/campus/notices`
- Academic APIs: `/api/academics/courses`, `/attendance`, `/timetable`, `/assignments`, `/exams`
- Faculty/admin content creation: `/api/campus/events`, `/api/campus/notices`, academic POST routes
- Document intelligence: `/api/documents/upload`, `/api/documents`, `/api/shaan/chat`
- Admin: `/api/admin/users`, `/api/admin/audit`, role update endpoint

## Roles
Public registration creates student accounts only. Promote faculty/admin accounts through a trusted local database process for development; never expose public role assignment in production. Use separate accounts to test each role.

## ML training
`python -m app.ml.train` saves the model. `python -m app.ml.evaluate` prints a deterministic stratified holdout report. Data is synthetic starter material; report only measured results and validate with representative anonymized queries.

## Production checklist
Replace the development JWT secret, use HTTPS and strict CORS, add rate limiting and monitoring, set up database migrations and PostgreSQL for multi-user production, harden file uploads, configure backups, and review privacy obligations before using real student records. AI-generated answers can be wrong; official policies must be grounded in verified sources.

## Tests
From `backend`, run `pytest -q`. Then exercise the API using `/docs` and separate student/faculty/admin accounts.

## Docker local deployment
Install Docker Desktop, then from the project root create a `.env` file with a long random secret, for example `JWT_SECRET=...` and optionally `GEMINI_API_KEY=...`. Run:
```powershell
docker compose up --build
```
Open `http://localhost:8080`. SQLite persists in the `campusverse_data` Docker volume. This is a reproducible single-machine deployment, not a public cloud deployment. For internet-facing use, configure HTTPS, managed secrets, backups, rate limiting and a managed database.

## Local role promotion (development only)
Register the account first, then from `backend` run `python -m scripts.promote_user your-email@example.com admin` or use `faculty`. This script requires trusted shell access and is not exposed as a public API. Sign out and sign in again after changing roles.

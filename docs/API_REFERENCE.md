# API quick reference

Base URL during local development: `http://127.0.0.1:8000`. Interactive docs: `/docs`.

| Method | Path | Access | Purpose |
|---|---|---|---|
| GET | `/api/health` | Public | Service health |
| POST | `/api/auth/register` | Public | Create student account |
| POST | `/api/auth/login` | Public | Sign in; returns bearer token |
| GET | `/api/auth/me` | Authenticated | Current account |
| GET | `/api/dashboard` | Public | Dashboard event/notice summary |
| GET | `/api/campus/events` | Public | Event list |
| GET | `/api/campus/notices` | Public | Notice list |
| GET/POST | `/api/academics/courses` | Auth / faculty or admin for POST | List/create courses |
| GET/POST | `/api/academics/attendance` | Auth / faculty or admin for POST | Read own attendance or mark attendance |
| GET | `/api/academics/timetable` | Authenticated | Cohort timetable |
| GET/POST | `/api/academics/assignments` | Auth / faculty or admin for POST | List/create assignments |
| POST | `/api/academics/assignments/{id}/submit` | Student | Submit/update own assignment |
| GET/POST | `/api/academics/exams` | Auth / faculty or admin for POST | List/create exams |
| POST | `/api/campus/notices` | Faculty/admin | Publish notice |
| POST | `/api/campus/events` | Faculty/admin | Publish event |
| POST | `/api/documents/upload` | Faculty/admin | Index PDF/TXT/MD text for SHAAN |
| GET | `/api/documents` | Faculty/admin | List indexed documents |
| DELETE | `/api/documents/{id}` | Admin | Delete indexed document |
| POST | `/api/shaan/chat` | Authenticated | Ask SHAAN; accepts message and optional session ID |
| GET | `/api/shaan/history/{session_id}` | Authenticated | Own conversation history |
| GET | `/api/admin/users` | Admin | List accounts |
| PATCH | `/api/admin/users/{id}/role?role=faculty` | Admin | Change role |
| GET | `/api/admin/audit` | Admin | Recent audit events |

Send `Authorization: Bearer <access_token>` for protected routes. Public registration intentionally never accepts a role field.

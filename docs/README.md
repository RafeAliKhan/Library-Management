# Library Management App

Flask + SQLite backend, vanilla HTML/CSS/JS frontend. JWT auth, bcrypt hashing, role-based access (member / librarian).
---
## Structure
- `backend/app.py` – app entry, serves the frontend
- `backend/routes/` – auth, books (CRUD), loans (borrow/return/fines/overdue)
- `backend/auth.py` – JWT + `@login_required` / `@librarian_required` (RBAC)
- `backend/validation.py` – input checks
- `backend/schema.sql` – users, books, loans tables
- `frontend/` – login, dashboard (live search), profile, admin pages

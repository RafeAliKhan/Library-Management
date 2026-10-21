# Library Management App

Flask + SQLite backend, vanilla HTML/CSS/JS frontend. JWT auth, bcrypt hashing, role-based access (member / librarian).

## Run
```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd backend
python seed.py      # sample data + demo accounts
python app.py       # http://localhost:5000
```
Demo logins: `admin@library.com / admin123` (librarian), `member@library.com / member123`.

## Structure
- `backend/app.py` – app entry, serves the frontend
- `backend/routes/` – auth, books (CRUD), loans (borrow/return/fines/overdue)
- `backend/auth.py` – JWT + `@login_required` / `@librarian_required` (RBAC)
- `backend/validation.py` – input checks
- `backend/schema.sql` – users, books, loans tables
- `frontend/` – login, dashboard (live search), profile, admin pages

## Ideas to extend
- Email alerts for overdue books (SendGrid / smtplib)
- QR codes for checkout (`qrcode` lib)
- Swap SQLite for PostgreSQL; deploy on Render/Railway (use gunicorn, set SECRET_KEY)
- Tests with pytest, "pay fine" endpoint, pagination, book cover images

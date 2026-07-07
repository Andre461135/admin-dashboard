# AI-Python-Admin-Dashboard

A premium, production-ready **AI-powered Admin Dashboard** built with **Python, Flask, and Vanilla JavaScript**. Features a modern glassmorphism UI with dark/light mode, comprehensive management tools, and built-in AI-powered insights.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-black)
![License](https://img.shields.io/badge/License-MIT-green)
![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-success)

**Live Demo (Static UI):** [https://sers457.github.io/AI-Python-Admin-Dashboard/](https://sers457.github.io/AI-Python-Admin-Dashboard/)

---

## Features

### Authentication
- Secure login with password hashing (Werkzeug)
- Session management with Flask-Login
- Remember me functionality
- Forgot password flow
- CSRF protection (Flask-WTF)

### Dashboard
- Revenue analytics with interactive charts (Chart.js)
- User statistics and activity feed
- Real-time notifications
- Performance metrics
- AI-powered dashboard insights
- Quick action tasks

### User Management
- Full CRUD operations (Create, Read, Update, Delete)
- Search, filter, and pagination
- Role management (admin, moderator, user)
- Status management (active, inactive, suspended)
- Profile image upload with validation

### Product Management
- Full CRUD operations
- Category management
- Inventory tracking with visual indicators
- Product image upload

### Reports
- Users, Sales, Products, Revenue reports
- **CSV export** - Download report data as CSV files
- **PDF export** - Download styled PDF reports via ReportLab
- AI-generated report summaries
- Interactive report preview

### AI Assistant
- Dashboard insights generation
- Sales trend summaries
- Smart search across users, products, transactions
- Trend analysis (30-day patterns)
- Interactive rule-based chatbot
- **Designed for easy OpenAI/LLM API integration** — replace `_call_llm()` in `ai_helpers.py`

### Security
| Feature | Implementation |
|---------|---------------|
| Password hashing | Werkzeug `generate_password_hash` |
| CSRF protection | Flask-WTF |
| SQL injection | SQLAlchemy ORM (parameterized queries) |
| XSS protection | Jinja2 auto-escaping |
| Secure sessions | Flask-Login with signed cookies |
| Input validation | Server-side sanitization |
| File uploads | Extension whitelist + UUID rename |
| Error handling | Try/except wrappers + flash messages |

---

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| Python 3.8+ | Core programming language |
| Flask 3.0 | Web framework |
| SQLite | Database (auto-created, auto-seeded) |
| SQLAlchemy 2.0 | ORM |
| Flask-Login | Session management |
| Flask-WTF | CSRF protection |
| HTML5 + CSS3 | Structure and styling |
| Vanilla JavaScript | Frontend interactivity |
| Chart.js | Data visualization |
| ReportLab | PDF generation |

---

## Project Structure

```
AI-Python-Admin-Dashboard/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── database/
│   │   └── schema.py            # DB init & 13-user/12-product seed
│   ├── models/
│   │   └── models.py            # User, Product, Activity, Notification, Transaction, Report
│   ├── routes/
│   │   ├── auth.py              # Login, logout, forgot password
│   │   ├── dashboard.py         # Overview, charts, stats, insights
│   │   ├── users.py             # CRUD, search, pagination, roles
│   │   ├── products.py          # CRUD, categories, inventory
│   │   ├── reports.py           # View, CSV export, PDF export
│   │   ├── settings.py          # Password, theme, profile, notifications
│   │   └── ai.py                # AI insights, chatbot, search, trends
│   ├── static/
│   │   ├── css/style.css        # 38KB glassmorphism stylesheet
│   │   └── javascript/app.js    # Sidebar, search, theme, notifications
│   ├── templates/               # 11 Jinja2 templates
│   │   ├── base.html            # Layout with sidebar, topbar, notifications
│   │   ├── login.html           # Auth page
│   │   ├── dashboard.html       # Main dashboard with Chart.js
│   │   ├── users.html           # User list with filters
│   │   ├── user_form.html       # Add/edit user
│   │   ├── products.html        # Product list
│   │   ├── product_form.html    # Add/edit product
│   │   ├── reports.html         # Report cards + preview
│   │   ├── settings.html        # Password, theme, notifications
│   │   ├── profile.html         # Avatar, bio
│   │   └── ai_assistant.html    # Insights, summary, trends, chatbot
│   ├── uploads/                 # User uploaded images
│   └── utilities/
│       ├── helpers.py           # File upload, pagination
│       ├── decorators.py        # login_required, admin_only, handle_errors
│       └── ai_helpers.py        # AIAssistant class (OpenAI-ready)
├── docs/                        # GitHub Pages static site
│   ├── index.html               # Landing page
│   ├── dashboard.html           # Static dashboard demo
│   └── login.html               # Static login demo
├── .github/workflows/
│   └── pages.yml                # GitHub Actions → GitHub Pages deploy
├── database/                    # SQLite DB (auto-created)
├── run.py                       # Entry point
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker build
├── docker-compose.yml           # Docker Compose
├── Procfile                     # Gunicorn (Render/Railway)
├── .env.example                 # Environment variables template
├── .gitignore
├── README.md
├── LICENSE                      # MIT
├── CONTRIBUTING.md
└── CHANGELOG.md
```

---

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### 1. Clone

```bash
git clone https://github.com/sers457/AI-Python-Admin-Dashboard.git
cd AI-Python-Admin-Dashboard
```

### 2. Install

```bash
pip install -r requirements.txt
```

### 3. Run

```bash
python run.py
```

The app will:
- Create the SQLite database automatically at `database/admin.db`
- Seed it with realistic sample data (13 users, 12 products, 12 transactions)
- Start on **http://localhost:5000**

### 4. Login

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123` | Admin |

---

## GitHub Pages (Static Demo)

A static UI demo is live at:

**https://sers457.github.io/AI-Python-Admin-Dashboard/**

| Page | Description |
|------|-------------|
| `/` | Landing page with project overview |
| `/dashboard.html` | Interactive dashboard with Chart.js |
| `/login.html` | Login page showcase |

The static site is built from the `docs/` folder and auto-deploys via GitHub Actions on every push to `master`.

---

## Deployment

### Docker

```bash
docker-compose up -d
```

### Render

1. Connect `https://github.com/sers457/AI-Python-Admin-Dashboard`
2. **Build:** `pip install -r requirements.txt`
3. **Start:** `gunicorn run:app --bind 0.0.0.0:$PORT`
4. Add env: `SECRET_KEY`

### Railway

1. Connect GitHub repo — Railway auto-detects `Procfile`
2. Add env: `SECRET_KEY`

### PythonAnywhere

1. Clone repo or upload files
2. Create manual web app
3. Set WSGI to `run.py`
4. Install deps in virtualenv

### Ubuntu VPS

```bash
pip install -r requirements.txt gunicorn
gunicorn run:app --bind 0.0.0.0:8000 --workers 4
# Configure Nginx as reverse proxy
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `dev-secret-key-change-in-production` | Flask signing key |
| `DATABASE_URL` | `sqlite:///database/admin.db` | Database URI |
| `FLASK_DEBUG` | `1` | Debug mode |
| `PORT` | `5000` | Server port |

Copy `.env.example` → `.env` and customize for production.

---

## Git Commands (Manual Setup)

```bash
git init
git add .
git commit -m "Initial commit: AI-powered admin dashboard"
git remote add origin https://github.com/sers457/AI-Python-Admin-Dashboard.git
git push -u origin master
```

---

## Connecting to OpenAI

The AI module (`app/utilities/ai_helpers.py`) is designed to be OpenAI-ready.
Replace the `_call_llm` method:

```python
import openai

@staticmethod
def _call_llm(prompt):
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

---

## License

MIT License — see [LICENSE](LICENSE).

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

---

Built with Python, Flask, and passion.

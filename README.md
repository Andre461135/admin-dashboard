# AdminPro - AI-Powered Admin Dashboard

A premium, production-ready, AI-powered admin dashboard built with **Python, Flask, and Vanilla JavaScript**. Features a modern glassmorphism UI with dark/light mode, comprehensive management tools, and built-in AI-powered insights.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-black)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

### Authentication
- Secure login with password hashing
- Session management with Flask-Login
- Remember me functionality
- Forgot password flow
- CSRF protection

### Dashboard
- Revenue analytics with interactive charts (Chart.js)
- User statistics and activity feed
- Real-time notifications
- Performance metrics
- AI-powered dashboard insights
- Quick action tasks

### User Management
- Full CRUD operations
- Search, filter, and pagination
- Role management (admin, moderator, user)
- Status management (active, inactive, suspended)
- Profile image upload

### Product Management
- Full CRUD operations
- Category management
- Inventory tracking with visual indicators
- Product image upload

### Reports
- Users, Sales, Products, Revenue reports
- CSV export
- AI-generated report summaries
- Interactive report preview

### AI Assistant
- Dashboard insights generation
- Sales trend summaries
- Smart search across users, products, transactions
- Trend analysis
- Interactive chatbot
- Designed for easy OpenAI/LLM API integration

### Security
- Password hashing (Werkzeug)
- CSRF protection (Flask-WTF)
- SQL injection protection (SQLAlchemy)
- XSS protection (Jinja2 auto-escaping)
- Secure file uploads with validation
- Proper error handling

---

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| Python 3.8+ | Core programming language |
| Flask 3.0 | Web framework |
| SQLite | Database |
| SQLAlchemy | ORM |
| Flask-Login | Session management |
| Flask-WTF | CSRF protection |
| HTML5 + CSS3 | Structure and styling |
| Vanilla JS | Frontend interactivity |
| Chart.js | Data visualization |

---

## Project Structure

```
admin-dashboard/
├── app/
│   ├── __init__.py          # App factory
│   ├── database/
│   │   └── schema.py        # DB initialization & seeding
│   ├── models/
│   │   └── models.py        # SQLAlchemy models
│   ├── routes/
│   │   ├── auth.py          # Authentication routes
│   │   ├── dashboard.py     # Dashboard routes
│   │   ├── users.py         # User management routes
│   │   ├── products.py      # Product management routes
│   │   ├── reports.py       # Reports & export routes
│   │   ├── settings.py      # Settings & profile routes
│   │   └── ai.py            # AI feature routes
│   ├── static/
│   │   ├── css/style.css    # Complete stylesheet
│   │   └── javascript/app.js # Frontend interactivity
│   ├── templates/           # Jinja2 templates
│   └── utilities/
│       ├── helpers.py       # Utility functions
│       ├── decorators.py    # Route decorators
│       └── ai_helpers.py    # AI assistant module
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker build
├── docker-compose.yml       # Docker Compose
├── Procfile                 # Heroku/Railway deploy
└── .env.example             # Environment variables
```

---

## Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/yourusername/admin-dashboard.git
cd admin-dashboard
pip install -r requirements.txt
```

### 2. Run

```bash
python run.py
```

The app will:
- Create the SQLite database automatically
- Seed it with realistic sample data
- Start on `http://localhost:5000`

### 3. Login

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123` | Admin |

---

## Deployment

### Docker

```bash
docker-compose up -d
```

### Render

1. Connect your GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `gunicorn run:app --bind 0.0.0.0:$PORT`
4. Add environment variable: `SECRET_KEY`

### Railway

1. Connect GitHub repository
2. Railway auto-detects `Procfile`
3. Add `SECRET_KEY` environment variable

### PythonAnywhere

1. Upload files via Git or manual upload
2. Create a web app with manual configuration
3. Set WSGI file to point to `run.py`
4. Install dependencies in virtualenv

### Ubuntu VPS (Gunicorn + Nginx)

```bash
# Install dependencies
pip install -r requirements.txt gunicorn

# Run with Gunicorn
gunicorn run:app --bind 0.0.0.0:8000 --workers 4

# Configure Nginx as reverse proxy
# See: https://flask.palletsprojects.com/en/stable/deploying/
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | `dev-secret-key...` |
| `DATABASE_URL` | Database connection string | `sqlite:///database/admin.db` |
| `FLASK_DEBUG` | Debug mode (1 or 0) | `1` |
| `PORT` | Application port | `5000` |

Duplicate `.env.example` to `.env` and customize.

---

## Git Setup

```bash
git init
git add .
git commit -m "Initial commit: AI-powered admin dashboard"
git remote add origin https://github.com/yourusername/admin-dashboard.git
git push -u origin main
```

---

## License

MIT License - see [LICENSE](LICENSE) file.

---

## Screenshots

> Screenshots will be added in a future update.

---

Built with Python, Flask, and passion.

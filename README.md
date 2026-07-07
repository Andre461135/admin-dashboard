# AI-Powered Admin Dashboard

A premium, production-ready, AI-powered admin dashboard built with Python, Flask, and vanilla JavaScript. Features a modern glassmorphism UI, dark/light mode, real-time analytics, user management, product management, report generation, and AI-powered insights.

## Features

### Dashboard
- Real-time analytics and statistics
- Interactive charts (bar, line, doughnut)
- Live activity feed
- AI-powered insights and recommendations
- Smart search across users and products
- AI assistant for natural-language queries

### User Management
- Full CRUD operations
- Role-based access (Admin, Editor, User)
- Status management (Active, Inactive, Suspended)
- Profile image upload
- Search and pagination

### Product Management
- Full CRUD operations
- Category management
- Inventory tracking
- Product image upload
- Search and filter by category

### Reports
- Users, Sales, Products, and Revenue reports
- CSV export
- PDF export with professional formatting
- AI-generated report summaries

### Settings
- Profile management
- Password change
- Theme toggle (Light/Dark)
- Notification preferences

### Security
- Password hashing (Werkzeug)
- CSRF protection (Flask-WTF)
- SQL injection protection (SQLAlchemy)
- XSS prevention (Jinja2 auto-escaping)
- Secure file upload validation
- HTTP-only session cookies
- Input validation (WTForms)

## Tech Stack

- **Backend:** Python, Flask, SQLAlchemy, Flask-Login
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Database:** SQLite (default), PostgreSQL-ready
- **Charts:** Custom vanilla JS canvas charts
- **PDF:** ReportLab
- **Deployment:** Gunicorn, Docker, Nginx

## Quick Start

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/admin-dashboard.git
cd admin-dashboard

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

The application will be available at `http://localhost:5000`.

### Demo Accounts

| Email | Password | Role |
|-------|----------|------|
| admin@dashboard.com | admin123 | Admin |
| demo@dashboard.com | demo123 | User |

## Project Structure

```
admin-dashboard/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── forms.py             # WTForms
│   ├── utils.py             # Utility functions & seed data
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── insights.py      # AI insight generation
│   │   └── assistant.py     # AI chat assistant
│   ├── routes/
│   │   ├── auth.py          # Authentication routes
│   │   ├── dashboard.py     # Dashboard routes
│   │   ├── users.py         # User management routes
│   │   ├── products.py      # Product management routes
│   │   ├── reports.py       # Report generation routes
│   │   ├── settings.py      # Settings routes
│   │   └── api.py           # API & AI endpoints
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css    # Premium dashboard CSS
│   │   ├── js/
│   │   │   └── app.js       # Dashboard JavaScript
│   │   └── uploads/         # Uploaded files
│   ├── templates/
│   │   ├── base.html        # Base template
│   │   ├── auth/            # Login & forgot password
│   │   ├── dashboard/       # Dashboard & analytics
│   │   ├── users/           # User management
│   │   ├── products/        # Product management
│   │   ├── reports/         # Reports
│   │   └── settings/        # Settings
│   └── database/
│       └── admin.db         # SQLite database (auto-created)
├── config.py                # Application configuration
├── run.py                   # Entry point
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose
├── Procfile                 # Heroku/Railway deployment
├── .env.example             # Environment variables template
└── .gitignore
```

## Deployment

### Deploy to Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Use the following settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app`
4. Add environment variable: `SECRET_KEY=your-secret-key`

### Deploy to Railway

1. Create a new project on Railway
2. Connect your GitHub repository
3. Railway auto-detects Python and uses `gunicorn run:app`

### Deploy to PythonAnywhere

1. Upload files to PythonAnywhere
2. Create a web app with manual config
3. Set WSGI file to point to `run.py`
4. Install dependencies in a virtualenv

### Deploy to Ubuntu VPS

```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv nginx

# Clone and setup
git clone https://github.com/yourusername/admin-dashboard.git
cd admin-dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with Gunicorn
gunicorn --workers 4 --bind 0.0.0.0:8000 run:app

# Nginx configuration
sudo nano /etc/nginx/sites-available/dashboard
```

Example Nginx config:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/admin-dashboard/app/static/;
    }
}
```

### Docker Deployment

```bash
docker-compose up -d
```

## AI Features

The dashboard includes built-in AI features powered by Python:

- **Dashboard Insights:** Automated analysis of user growth, inventory, revenue, and trends
- **Sales Trend Summaries:** Natural-language summaries of sales performance
- **Smart Search:** Search across users and products with intelligent results
- **Report Summaries:** Auto-generated summaries for each report type
- **AI Assistant:** Natural-language chat interface for querying platform data

The AI layer is designed to be easily upgraded to use OpenAI, Anthropic, or any LLM API by modifying the `app/ai/` modules.

## GitHub Setup

```bash
# Initialize Git
git init
git add .
git commit -m "Initial commit: AI-powered admin dashboard"

# Create repository on GitHub (via web UI)

# Add remote and push
git remote add origin https://github.com/yourusername/admin-dashboard.git
git branch -M main
git push -u origin main
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

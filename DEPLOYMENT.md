# Deployment Guide - Fergani OCR

This guide covers deploying the Fergani OCR application to various cloud platforms.

## Table of Contents

- [Railway.app (Recommended)](#railwayapp-recommended)
- [Render.com](#rendercom)
- [Fly.io](#flyio)
- [Environment Variables](#environment-variables)
- [Production Checklist](#production-checklist)

---

## Railway.app (Recommended)

Railway is the easiest and most developer-friendly platform for Django apps.

### Prerequisites

- GitHub/GitLab account
- Railway account (sign up at https://railway.app)

### Step 1: Prepare Your Code

1. **Update requirements.txt**

```bash
cd /home/ahadjon/work/fergani/fergani-ocr
pip freeze > requirements.txt

# Add these production dependencies if not present:
echo "gunicorn==21.2.0" >> requirements.txt
echo "psycopg2-binary==2.9.9" >> requirements.txt
echo "whitenoise==6.6.0" >> requirements.txt
echo "dj-database-url==2.1.0" >> requirements.txt
```

2. **Update Django settings** (already done, see below)

3. **Push to GitHub**

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/fergani-ocr.git
git push -u origin main
```

### Step 2: Deploy to Railway

1. Go to https://railway.app
2. Click "Start a New Project"
3. Choose "Deploy from GitHub repo"
4. Select your `fergani-ocr` repository
5. Railway will auto-detect Django and start deployment

### Step 3: Add PostgreSQL Database

1. In your Railway project, click "New" → "Database" → "PostgreSQL"
2. Railway will automatically set `DATABASE_URL` environment variable

### Step 4: Set Environment Variables

In Railway dashboard, go to your service → Variables:

```bash
SECRET_KEY=your-super-secret-key-here-generate-new-one
DEBUG=False
ALLOWED_HOSTS=your-app.up.railway.app
CSRF_TRUSTED_ORIGINS=https://your-app.up.railway.app
```

### Step 5: Deploy!

Railway automatically deploys on every push to main branch.

**Your app will be available at:** `https://your-app.up.railway.app`

---

## Render.com

### Step 1: Create render.yaml

Create this file in your project root (already created below).

### Step 2: Deploy

1. Go to https://render.com
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will read `render.yaml` and set up everything

### Step 3: Set Environment Variables

In Render dashboard:

- `SECRET_KEY`: Generate a strong secret key
- `DEBUG`: False
- `ALLOWED_HOSTS`: your-app.onrender.com

---

## Fly.io

### Step 1: Install Fly CLI

```bash
curl -L https://fly.io/install.sh | sh
```

### Step 2: Login and Initialize

```bash
fly auth login
cd /home/ahadjon/work/fergani/fergani-ocr
fly launch
```

### Step 3: Configure Dockerfile

Fly will generate a Dockerfile. Make sure it includes Tesseract:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-ara \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY fergani/ /app/
RUN python manage.py collectstatic --no-input

CMD ["gunicorn", "fergani.wsgi:application", "--bind", "0.0.0.0:8080"]
```

### Step 4: Deploy

```bash
fly deploy
```

---

## Environment Variables

### Required for Production

```bash
# Security
SECRET_KEY=your-secret-key-min-50-characters-long
DEBUG=False

# Hosts
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com

# Database (auto-set by platform usually)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Optional
DJANGO_SETTINGS_MODULE=fergani.settings
```

### Generate SECRET_KEY

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Production Checklist

### 1. Update `fergani/settings.py`

Add this at the top:

```python
import os
import dj_database_url
from pathlib import Path

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
```

Add at the bottom:

```python
# Database
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# WhiteNoise middleware (add after SecurityMiddleware)
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
```

### 2. Create `.env.example`

```bash
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
```

### 3. Update `.gitignore`

```bash
*.pyc
__pycache__/
*.sqlite3
db.sqlite3
.env
.venv/
venv/
media/
staticfiles/
*.log
.DS_Store
```

---

## Cost Comparison

| Platform           | Free Tier       | Database      | Storage       | Best For                       |
| ------------------ | --------------- | ------------- | ------------- | ------------------------------ |
| **Railway**        | $5 credit/month | ✅ PostgreSQL | ✅ Persistent | Development & Small Production |
| **Render**         | ✅ Free tier    | ✅ PostgreSQL | ⚠️ Ephemeral  | Development                    |
| **Fly.io**         | Generous free   | ✅ PostgreSQL | ✅ Persistent | Production-ready               |
| **PythonAnywhere** | Limited free    | ⚠️ MySQL only | ✅ Persistent | Simple Django apps             |

---

## Quick Start - Railway (Fastest)

```bash
# 1. Install dependencies
pip install gunicorn psycopg2-binary whitenoise dj-database-url

# 2. Update requirements.txt
pip freeze > requirements.txt

# 3. Push to GitHub
git init
git add .
git commit -m "Initial commit"
git push

# 4. Deploy on Railway
# - Connect GitHub repo
# - Add PostgreSQL database
# - Set environment variables
# - Deploy!
```

**That's it! Your app will be live in 5-10 minutes.**

---

## Support & Troubleshooting

### Common Issues

**Issue: Tesseract not found**

- Solution: Make sure `tesseract-ocr` is in your platform's package list

**Issue: Database connection error**

- Solution: Check `DATABASE_URL` environment variable is set

**Issue: Static files not loading**

- Solution: Run `python manage.py collectstatic` before deployment

**Issue: Media files disappearing (Render)**

- Solution: Use external storage like AWS S3 or Cloudinary for production

### Getting Help

- Railway: https://railway.app/help
- Render: https://render.com/docs
- Fly.io: https://fly.io/docs

---

**Ready to deploy? Choose Railway for the easiest experience! 🚀**

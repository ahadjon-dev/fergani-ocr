# Railway Deployment Guide

## Understanding the Setup

After thorough review of Railway's documentation, here's the correct configuration:

### Key Facts

1. **Nixpacks is DEPRECATED** - Railway now uses **Railpack** by default
2. **Django Auto-Detection**: Railway automatically detects Django projects when it finds `manage.py` and `requirements.txt`
3. **System Dependencies**: Use `nixpacks.toml` for system packages (works with Railpack)
4. **Root Directory**: Set to `fergani` in Railway UI, so all paths are relative to that directory

## Configuration Files

### 1. `railway.json` (REQUIRED - in fergani/ directory)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "RAILPACK",
    "nixpacksConfigPath": "nixpacks.toml"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && gunicorn fergani.wsgi:application --bind 0.0.0.0:${PORT:-8000}",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Explanation:**

- `builder: "RAILPACK"` - Uses the new Railpack builder (NOT deprecated Nixpacks)
- `nixpacksConfigPath` - Points to system dependencies config
- `startCommand` - Runs migrations then starts Gunicorn
- `restartPolicyType` - Restarts on failure, max 10 retries

### 2. `nixpacks.toml` (REQUIRED - in fergani/ directory)

```toml
[phases.setup]
aptPkgs = ["tesseract-ocr", "tesseract-ocr-eng", "tesseract-ocr-ara", "poppler-utils", "libpq-dev"]

[start]
cmd = "python manage.py migrate && gunicorn fergani.wsgi:application --bind 0.0.0.0:${PORT:-8000}"
```

**Explanation:**

- Installs Tesseract OCR with English and Arabic language packs
- Installs Poppler for PDF processing
- Installs libpq-dev for PostgreSQL support

### 3. `Procfile` (OPTIONAL - backup if railway.json fails)

```
web: python manage.py migrate && gunicorn fergani.wsgi:application --bind 0.0.0.0:$PORT
```

### 4. `requirements.txt` (REQUIRED - in fergani/ directory)

Already exists with all dependencies including:

- Django 5.0.1
- gunicorn 21.2.0
- psycopg2-binary 2.9.9
- whitenoise 6.11.0
- etc.

### 5. `runtime.txt` (REQUIRED - in fergani/ directory)

```
python-3.11.9
```

## Railway Dashboard Configuration

### Service Settings

1. **Root Directory**: `fergani`

   - Navigate to: Service → Settings → Source
   - Set: Root Directory = `fergani`
   - This tells Railway that your Django project is in the `fergani/` subdirectory

2. **Environment Variables** (Service → Variables)

   ```
   SECRET_KEY=<generate-using-command-below>
   DEBUG=False
   ALLOWED_HOSTS=<your-app>.up.railway.app
   CSRF_TRUSTED_ORIGINS=https://<your-app>.up.railway.app
   DATABASE_URL=<auto-set-by-postgresql-plugin>
   ```

   **Generate SECRET_KEY:**

   ```bash
   cd /home/ahadjon/work/fergani/fergani-ocr/fergani
   source /home/ahadjon/work/fergani/venv/bin/activate
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```

3. **PostgreSQL Database**
   - In Railway Dashboard: Project → New → Database → PostgreSQL
   - Railway automatically sets `DATABASE_URL` environment variable
   - No manual configuration needed

## Deployment Steps

### 1. Commit Changes

```bash
cd /home/ahadjon/work/fergani/fergani-ocr/fergani
git add railway.json nixpacks.toml Procfile runtime.txt requirements.txt
git commit -m "chore: Configure Railway deployment with Railpack"
git push origin feature/setup-root
```

### 2. Configure Railway (First Time Only)

1. Go to Railway Dashboard
2. Select your project
3. Click on your service
4. Go to Settings → Source
5. Set **Root Directory** to: `fergani`
6. Click "Save"

### 3. Set Environment Variables

1. Go to Service → Variables
2. Add each variable listed above
3. Click "Add" after each one

### 4. Add PostgreSQL Database

1. Click "+ New" in your project
2. Select "Database"
3. Choose "PostgreSQL"
4. Railway automatically links it to your service

### 5. Deploy

- Railway will automatically deploy when you push to GitHub
- Or manually trigger: Service → Deployments → "Deploy"

## Build Process (What Railway Does)

1. **Detects Django**: Finds `manage.py` and `requirements.txt`
2. **Installs System Packages**: Uses `nixpacks.toml` to install Tesseract, Poppler, PostgreSQL dev libs
3. **Creates Virtual Environment**: Creates Python venv at `/opt/venv`
4. **Installs Python Dependencies**: Runs `pip install -r requirements.txt`
5. **Runs Start Command**: Executes migrations and starts Gunicorn

## Expected Build Logs

You should see:

```
====================
Using Railpack!
====================

Building in /app/
Detected: Python Django Application
Installing system packages...
Installing Python dependencies...
Build completed successfully!

Deployment starting...
Running migrations...
Starting Gunicorn server...
```

## Troubleshooting

### "Script start.sh not found" or "Railpack could not determine how to build"

**Cause**: Railway can't find `manage.py` or `requirements.txt`

**Solution**:

- Verify Root Directory is set to `fergani`
- Ensure `manage.py` and `requirements.txt` are in the `fergani/` directory
- Check that files are committed to Git

### "pip: command not found"

**Cause**: Using deprecated NIXPACKS builder

**Solution**:

- Change `"builder": "RAILPACK"` in `railway.json`
- Railway auto-installs pip with Railpack

### "ModuleNotFoundError: No module named 'fergani'"

**Cause**: Working directory is incorrect

**Solution**:

- Ensure Root Directory = `fergani` in Railway UI
- Check `startCommand` uses correct path: `gunicorn fergani.wsgi:application`

### Database Connection Errors

**Cause**: PostgreSQL not added or DATABASE_URL not set

**Solution**:

- Add PostgreSQL database in Railway
- Verify `DATABASE_URL` is set in environment variables

## Verification

After deployment:

1. **Check Build Logs**: Should show "Build completed successfully"
2. **Check Deploy Logs**: Should show migrations running and Gunicorn starting
3. **Test Endpoint**: `https://<your-app>.up.railway.app/api/ocr/extract/`
4. **Check Admin**: `https://<your-app>.up.railway.app/admin/`

## Production Checklist

- [x] `DEBUG=False` set
- [x] `SECRET_KEY` is strong and unique
- [x] `ALLOWED_HOSTS` includes Railway domain
- [x] `CSRF_TRUSTED_ORIGINS` includes Railway domain
- [x] PostgreSQL database added
- [x] Static files served via WhiteNoise
- [x] Gunicorn configured with proper workers
- [x] Tesseract OCR languages installed (eng, ara)
- [x] Migrations run automatically on deploy
- [x] Restart policy configured (ON_FAILURE, max 10 retries)

## References

- [Railway Documentation](https://docs.railway.app/)
- [Railpack vs Nixpacks](https://docs.railway.app/reference/railpack)
- [Config as Code](https://docs.railway.app/reference/config-as-code)
- [Django on Railway](https://docs.railway.app/guides/django)
- [Python Provider](https://nixpacks.com/docs/providers/python)

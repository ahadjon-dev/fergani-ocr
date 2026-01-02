# Railway Deployment Checklist

## Current Status

✅ Build: **SUCCESSFUL** - All dependencies installed  
❌ Deploy: **FAILING** - Healthcheck not responding

## The Issue

The healthcheck at `/api/ocr/health/` is timing out. This could be because:

1. **App is crashing on startup** - Check Deploy Logs in Railway
2. **Database not configured** - Need to add PostgreSQL or allow SQLite
3. **Gunicorn not binding correctly** - PORT environment variable issue
4. **Healthcheck endpoint too slow** - Tesseract version check might timeout

## Immediate Actions Required

### 1. Check Deploy Logs in Railway Dashboard

Go to: Railway Dashboard → Your Service → **Deploy Logs** tab

Look for errors like:

- `ModuleNotFoundError` - Missing Python package
- `django.core.exceptions.ImproperlyConfigured` - Settings issue
- `django.db.utils.OperationalError` - Database connection issue
- Any Python tracebacks

### 2. Set Required Environment Variables

**Minimum to start:**

```bash
# In Railway Dashboard → Service → Variables

SECRET_KEY=your-generated-secret-key-here
ALLOWED_HOSTS=*.railway.app
DEBUG=True
```

**Generate SECRET_KEY locally:**

```bash
cd /home/ahadjon/work/fergani/fergani-ocr/fergani
source /home/ahadjon/work/fergani/venv/bin/activate
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 3. Add PostgreSQL Database (Optional but Recommended)

In Railway Dashboard:

1. Click "+ New"
2. Select "Database" → "PostgreSQL"
3. Railway automatically sets `DATABASE_URL`

**Note:** App will work with SQLite if no DATABASE_URL is set, but PostgreSQL is better for production.

### 4. Disable Healthcheck Temporarily (For Testing)

If the app starts but healthcheck still fails, you can disable it temporarily:

**Option A: Remove from railway.json**

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

**Option B: In Railway UI**

- Go to Service → Settings → Deploy
- Find "Health Check Path"
- Clear the value and save

### 5. Alternative: Create Simple Health Endpoint

If `/api/ocr/health/` is too slow (calls Tesseract), create a simpler one:

**Add to `fergani/urls.py`:**

```python
from django.http import JsonResponse

def simple_health(request):
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    path('health/', simple_health, name='simple_health'),
    # ... rest of urls
]
```

Then update `railway.json`:

```json
"healthcheckPath": "/health/"
```

## Common Issues & Solutions

### Issue: "Application failed to respond to HTTP requests"

**Cause:** Gunicorn not binding to Railway's PORT variable

**Solution:** Ensure start command uses `${PORT}`:

```bash
gunicorn fergani.wsgi:application --bind 0.0.0.0:${PORT:-8000}
```

### Issue: "ALLOWED_HOSTS validation failed"

**Cause:** Railway domain not in ALLOWED_HOSTS

**Solution:** Set environment variable:

```
ALLOWED_HOSTS=*.railway.app,localhost
```

### Issue: "SECRET_KEY required"

**Cause:** No SECRET_KEY environment variable set

**Solution:** Generate and set SECRET_KEY (see step 2 above)

### Issue: "OperationalError: no such table"

**Cause:** Migrations not running

**Solution:** Start command includes migrate:

```bash
python manage.py migrate && gunicorn ...
```

### Issue: Healthcheck timeout after 100 seconds

**Cause:** App is slow to start (migrations running)

**Solution:** Increase healthcheck timeout in railway.json:

```json
"healthcheckTimeout": 300
```

## Verification Steps

After deploying:

1. **Check Build Logs** - Should show "Successfully Built!"
2. **Check Deploy Logs** - Look for errors during startup
3. **Test Health Endpoint** - Should return 200 OK
4. **Test Main App** - Visit your Railway URL

## Debug Commands

If deployment is successful but app not responding:

```bash
# Check if Gunicorn is running
ps aux | grep gunicorn

# Check which port app is listening on
netstat -tlnp | grep python

# Check app logs
tail -f /var/log/app.log
```

## Next Steps

1. ✅ Commit current changes (Procfile, railway.json fixed)
2. ⏳ Set environment variables in Railway (SECRET_KEY, ALLOWED_HOSTS)
3. ⏳ Check Deploy Logs for specific error messages
4. ⏳ Add PostgreSQL database
5. ⏳ Test deployment

## Files Status

- ✅ `railway.json` - Uses RAILPACK, has healthcheck config
- ✅ `nixpacks.toml` - System packages configured
- ✅ `Procfile` - Fixed (removed `cd fergani`)
- ✅ `requirements.txt` - All dependencies listed
- ✅ `runtime.txt` - Python 3.11.9 specified

## Support Resources

- Railway Docs: https://docs.railway.app/
- Railway Discord: https://discord.gg/railway
- Django Deployment: https://docs.djangoproject.com/en/5.0/howto/deployment/
- Gunicorn Docs: https://docs.gunicorn.org/

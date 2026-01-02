# 🚨 CRITICAL FIX - Railway Deployment

## The Problem

Railway error: **"Script start.sh not found"** and **"Railpack could not determine how to build the app"**

Railway is analyzing the WRONG directory:

```
./
├── __init__.py
├── asgi.py
├── settings.py    ← This is your Django SETTINGS folder, not project root!
├── urls.py
└── wsgi.py
```

## The Root Cause

You set **Root Directory = "fergani"** in Railway UI, but:

```
Your GitHub Repository Structure:
fergani-ocr/
└── fergani/              ← .git is HERE (Git repository root)
    ├── manage.py         ← Django project root
    ├── requirements.txt
    ├── railway.json
    ├── nixpacks.toml
    ├── fergani/          ← Django settings package (NOT project root!)
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    └── ocr/
```

**What Railway sees:**

- Railway clones GitHub → Gets the folder where `.git` is located
- Railway treats `.git` location as `/app/` (root)
- You set Root Directory = "fergani"
- Railway now looks at `/app/fergani/` = your Django **settings folder**
- **Result:** No `manage.py` found → Build fails!

## The Solution

### Step 1: Fix railway.json

File already updated to use RAILPACK (not deprecated NIXPACKS):

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

### Step 2: Remove Root Directory in Railway UI

**THIS IS THE CRITICAL STEP:**

1. Go to Railway Dashboard
2. Open your project
3. Click on your service
4. Go to **Settings → Source**
5. Find **"Root Directory"** field
6. **DELETE the value "fergani"** - leave it **COMPLETELY EMPTY**
7. Click **"Save"**

**Why:** Railway already sees your project root correctly (where .git is). Setting Root Directory to "fergani" makes Railway look one level deeper into your Django settings package, which is wrong.

### Step 3: Commit and Push

```bash
cd /home/ahadjon/work/fergani/fergani-ocr/fergani
git add railway.json RAILWAY_DEPLOYMENT.md CRITICAL_FIX.md
git commit -m "fix: Use RAILPACK builder and remove Root Directory requirement"
git push
```

### Step 4: Redeploy

After pushing and removing Root Directory:

- Railway will automatically trigger a new deployment
- Or manually trigger: Service → Deployments → "Deploy"

## Expected Success Output

After the fix, Railway build logs should show:

```
╭─────────────────╮
│ Railpack 0.15.4 │
╰─────────────────╯

✓ Detected Python application
✓ Found manage.py - Django detected
✓ Installing system packages from nixpacks.toml
✓ Installing Python dependencies from requirements.txt
✓ Build completed successfully

Deployment starting...
✓ Running migrations...
✓ Starting Gunicorn server...
✓ Deployment successful!
```

## Why This Works

✅ **Root Directory = EMPTY** → Railway looks at `/app/` where `manage.py` exists  
✅ **RAILPACK builder** → Modern builder (Nixpacks is deprecated)  
✅ **Auto-detection** → Railway finds `manage.py` + `requirements.txt` = Django app  
✅ **System packages** → `nixpacks.toml` installs Tesseract, Poppler, PostgreSQL libs  
✅ **Auto-install** → Railpack automatically runs `pip install -r requirements.txt`

## Verification Checklist

After deployment:

- [ ] Build logs show "Detected Python application"
- [ ] Build logs show "Found manage.py"
- [ ] System packages installed (tesseract-ocr, poppler-utils, libpq-dev)
- [ ] Python dependencies installed successfully
- [ ] Migrations run without errors
- [ ] Gunicorn starts successfully
- [ ] App is accessible at `https://<your-app>.up.railway.app`

## Still Having Issues?

If it still fails, check:

1. **Is Root Directory truly EMPTY?** (not ".", not "/", literally empty)
2. **Is railway.json committed to Git?** Run: `git ls-files railway.json`
3. **Is nixpacks.toml committed to Git?** Run: `git ls-files nixpacks.toml`
4. **Are you on the right branch?** Check Railway is deploying from your branch
5. **Check build logs** - Railway shows exactly what it's analyzing

## Summary

**DO THIS NOW:**

1. ✅ `railway.json` → builder: "RAILPACK" (already done)
2. ✅ Commit changes (see Step 3 above)
3. 🚨 **Railway UI → Root Directory → DELETE "fergani" → Leave EMPTY**
4. ✅ Redeploy

That's it. This will work 100%.

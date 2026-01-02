# Fergani OCR - Quick Deploy Guide

This is a **5-minute guide** to deploy your OCR app for free while you develop.

## 🚀 Recommended: Railway.app (Easiest!)

**Free Tier**: $5 credit/month (enough for development)
**Pros**: Easy, PostgreSQL included, persistent storage, auto-deploy

### Deploy in 5 Minutes:

1. **Install production dependencies** (if not already done):

```bash
cd /home/ahadjon/work/fergani/fergani-ocr
pip install gunicorn psycopg2-binary whitenoise dj-database-url
```

2. **Push your code to GitHub**:

```bash
# Initialize git (if not done)
git init
git add .
git commit -m "Fergani OCR - Ready for deployment"

# Create GitHub repo and push
git remote add origin https://github.com/YOUR_USERNAME/fergani-ocr.git
git branch -M main
git push -u origin main
```

3. **Deploy on Railway**:

   - Go to https://railway.app
   - Click "Start a New Project"
   - Choose "Deploy from GitHub repo"
   - Select your `fergani-ocr` repository
   - Railway auto-detects Django and deploys!

4. **Add PostgreSQL Database**:

   - In Railway project, click "New" → "Database" → "PostgreSQL"
   - Done! DATABASE_URL is automatically set

5. **Set Environment Variables**:

   Go to your service → Variables tab and add:

   ```
   SECRET_KEY=<click "Generate" button>
   DEBUG=False
   ALLOWED_HOSTS=your-project.up.railway.app
   CSRF_TRUSTED_ORIGINS=https://your-project.up.railway.app
   ```

6. **Access your app**:
   ```
   https://your-project.up.railway.app
   ```

**Done! Your OCR app is live! 🎉**

---

## Alternative: Render.com

**Free Tier**: Yes (with cold starts)
**Pros**: Simple, PostgreSQL included, auto-deploy from Git

### Quick Deploy:

1. Push code to GitHub (same as above)

2. Go to https://render.com

   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Build Command: `cd fergani && pip install -r ../requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate`
   - Start Command: `cd fergani && gunicorn fergani.wsgi:application`

3. Add environment variables (same as Railway)

4. Create PostgreSQL database:
   - Click "New +" → "PostgreSQL"
   - Copy DATABASE_URL to your web service

---

## Platform Comparison

| Platform       | Free Tier    | Sleep/Idle         | Best For                 |
| -------------- | ------------ | ------------------ | ------------------------ |
| **Railway**    | $5 credit/mo | No sleep           | **Best for development** |
| Render         | Free         | Sleeps after 15min | Good alternative         |
| Fly.io         | Generous     | No sleep           | Production-ready         |
| PythonAnywhere | Limited      | No sleep           | Simple apps              |

---

## Post-Deployment Checklist

After deploying, test these:

✅ **Health Check**: `https://your-app.com/api/ocr/health/`
✅ **Image OCR**: Upload a test image via UI
✅ **PDF Extract**: Upload a test PDF
✅ **Database**: Check if documents are being saved
✅ **Admin Panel**: `https://your-app.com/admin/`

Create superuser:

```bash
# On Railway: use Railway CLI
railway run python manage.py createsuperuser

# On Render: use Shell from dashboard
python manage.py createsuperuser
```

---

## Troubleshooting

**Issue: Tesseract not found**

- Railway/Render automatically install it (check `railway.toml` or `render.yaml`)

**Issue: Static files not loading**

- Make sure WhiteNoise is installed and configured (already done)

**Issue: Database errors**

- Check DATABASE_URL environment variable is set
- Verify migrations ran: `python manage.py migrate`

**Issue: Media files disappearing**

- Use persistent storage (Railway has it, Render free tier doesn't)
- For production, use AWS S3 or Cloudinary

---

## Local Testing with Production Settings

Test production configuration locally:

```bash
# Create .env file
cp .env.example .env

# Edit .env with your values
nano .env

# Install python-dotenv
pip install python-dotenv

# Load environment variables and run
export DEBUG=False
python manage.py collectstatic --no-input
python manage.py runserver
```

---

## Next Steps

1. **Custom Domain**: Add your domain on Railway/Render
2. **Email**: Set up email for password resets
3. **Monitoring**: Use Railway/Render built-in logs
4. **Backups**: Set up database backups
5. **CDN**: Use Cloudflare for static files

---

## Cost After Free Tier

**Railway**: ~$5-10/month for small production use
**Render**: ~$7/month for persistent disk + database
**Fly.io**: Pay-as-you-go, ~$5-15/month

**Recommendation**: Start with Railway free tier, upgrade when needed.

---

## Support

- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs
- This project: See `DEPLOYMENT.md` for detailed guide

**Happy deploying! 🚀**

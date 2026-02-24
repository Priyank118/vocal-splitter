# Deploy to Render.com - Step by Step

## Prerequisites
- GitHub account with your code pushed
- Render account (free)

## Step 1: Push Code to GitHub

Your code is already committed! Verify it's on GitHub:
```bash
git log --oneline | head -5
git remote -v
```

You should see something like:
```
origin  https://github.com/YOUR_USERNAME/vocal-splitter-app.git
```

---

## Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Click "Sign Up" 
3. Choose "Sign up with GitHub"
4. Authorize Render to access your repositories

---

## Step 3: Create New Web Service

1. In Render dashboard, click **"New +"**
2. Select **"Web Service"**
3. Click **"Build and deploy from a Git repository"**

---

## Step 4: Connect GitHub Repository

1. Search for your repository: **vocal-splitter-app**
2. Click **"Connect"**
3. If not in the list, click **"Connect account"** and authorize Render on GitHub

---

## Step 5: Configure Service Settings

Fill in the form:

| Field | Value |
|-------|-------|
| **Name** | `vocal-splitter-app` |
| **Branch** | `main` |
| **Environment** | `Docker` |
| **Plan** | `Free` (or Paid if you want better performance) |

---

## Step 6: Add Environment Variables

Scroll down to **"Environment"** section and add:

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `FLASK_DEBUG` | `0` |
| `MAX_UPLOAD_SIZE` | `524288000` |

---

## Step 7: Configure Disk Storage (Important!)

Scroll to **"Disks"** section and add:

- **Name**: `volume` (or any name)
- **Mount Path**: `/app/output`
- **Size**: `10` GB (or more depending on your needs)

This stores audio files persistently.

---

## Step 8: Deploy

1. Click **"Create Web Service"** button at the bottom
2. Render will automatically:
   - Build your Docker image
   - Deploy the container
   - Provision a free domain

This takes **5-15 minutes** on first deploy (model downloads)

---

## Step 9: Monitor Deployment

1. Watch the **"Build & Deployment"** logs
2. You'll see:
   ```
   Building Docker image...
   ✓ Image built successfully
   Starting service...
   ✓ Service running on https://your-app-name.onrender.com
   ```

---

## Step 10: Test Your Deployment

Once deployed:
1. Go to your Render dashboard
2. Click the service name
3. Copy the **Service URL** (e.g., `https://your-app-name.onrender.com`)
4. Visit that URL in your browser
5. Test by uploading an audio file

---

## Important Notes

### First Deploy Takes Longer
- **First run**: 10-15 minutes (Spleeter models download ~300MB)
- **Subsequent runs**: Your uploads process normally

### Free Tier Limitations
- **Auto-shutdown**: Service sleeps after 15 minutes of inactivity
- **Limited resources**: ~0.5GB RAM (fine for small uploads)
- **No SLA**: Best for testing/hobby projects

### Upgrade When Needed
If you find limitations:
1. Edit service in Render dashboard
2. Change plan to **Starter** ($7/month) or higher
3. You'll get more resources and no auto-shutdown

---

## Common Issues & Solutions

### ❌ Build Fails with "Spleeter not found"
**Solution**: Models will download on first use. Build may timeout on free tier.
- Increase timeout in Dockerfile or upgrade plan

### ❌ Service is sleeping
**Solution**: Free tier auto-sleeps after 15 min inactivity.
- Upgrade to paid plan to keep running 24/7
- Or use periodic pings (cron jobs)

### ❌ Upload/Processing Timeout
**Solution**: Processing takes time.
- Increase timeout in Dockerfile (already set to 300s)
- For large files, upgrade to better plan

### ❌ Output files disappear
**Solution**: Must use persistent disk.
- Verify disk mounted at `/app/output` in Render dashboard
- Files should persist between deployments

### ❌ CORS errors
Check browser console - if seeing CORS errors:
- Ensure frontend API URL is `/upload` and `/download` (relative paths)
- Backend CORS is configured for `*`

---

## Updating Your App

After deployment, to update:

1. **Make changes locally**
   ```bash
   git add .
   git commit -m "Update: feature description"
   git push
   ```

2. **Render auto-redeploys** (watch dashboard for build progress)

3. **Or manual redeploy**:
   - Go to Render dashboard
   - Click "Manual Deploy" → "Latest Commit"

---

## Domain Setup (Optional)

To use custom domain (example.com):

1. In Render dashboard → Settings
2. Add custom domain
3. Update DNS records to point to Render
4. Render provides SSL certificate automatically (free!)

---

## Next Steps

✅ Deploy to Render (5-15 min)
✅ Test the app
✅ Share the link!

Questions? Check [Render docs](https://render.com/docs)

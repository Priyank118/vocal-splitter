# Deployment Guide - Vocal Splitter App

Your project is now ready for deployment! This guide covers multiple deployment options.

## Quick Start - Local Deployment with Docker

The easiest way to deploy is using Docker (requires Docker Desktop installed):

```bash
# Build and run with Docker Compose
docker-compose up --build
```

Access the app at `http://localhost:8000`

---

## Deployment Options

### Option 1: Render (Recommended - Free tier available)

1. **Create account** at [render.com](https://render.com)
2. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Deploy: Vocal Splitter App"
   git remote add origin https://github.com/YOUR_USERNAME/vocal-splitter-app.git
   git push -u origin main
   ```

3. **Create Web Service on Render**:
   - Connect your GitHub repo
   - Environment: Docker
   - Build Command: (leave default)
   - Start Command: (leave default)
   - Add environment variables:
     - `FLASK_ENV` = `production`

4. **Deploy!** Render will automatically build and deploy

---

### Option 2: Railway (Simple & Fast)

1. **Create account** at [railway.app](https://railway.app)
2. **Push to GitHub** (same as above)
3. **Connect repo** and deploy
4. Railway auto-detects Python/Docker and deploys

---

### Option 3: AWS (More Control)

#### Using Elastic Beanstalk:
1. Install AWS CLI
2. Create `.ebextensions/python.config`:
   ```yaml
   option_settings:
     aws:elasticbeanstalk:container:python:
       WSGIPath: app:app
   ```
3. Deploy: `eb deploy`

#### Using EC2:
```bash
# SSH into your instance
ssh -i your-key.pem ec2-user@YOUR_IP

# Install dependencies
sudo apt update
sudo apt install python3-pip docker.io nodejs npm
sudo docker-compose up -d
```

---

### Option 4: DigitalOcean App Platform

1. Create account at [digitalocean.com](https://digitalocean.com)
2. Create new App
3. Connect GitHub repo
4. Set build command: `docker-compose build`
5. Set run command: `docker-compose up`

---

### Option 5: Heroku (Traditional but Paid)

```bash
# Install Heroku CLI
npm install -g heroku

# Login
heroku login

# Create app
heroku create your-app-name

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

---

## Local Production Testing

Before deploying, test locally:

```bash
# Build frontend
cd splitter
npm run build
cd ..

# Build and run Docker
docker-compose up --build

# Visit http://localhost:8000
```

---

## Important Notes

### File Storage
- **Development**: Files stored locally in `uploads/` and `output/`
- **Production**: Use volume mounts or cloud storage (S3, etc.)

For cloud storage (optional):
```python
# Install boto3 for S3
pip install boto3

# Update app.py to use S3 instead of local storage
```

### Environment Variables

Create `.env` file for production:
```
FLASK_ENV=production
FLASK_DEBUG=0
MAX_UPLOAD_SIZE=524288000
```

### Model Downloads

Spleeter will automatically download models on first use (~300MB). This happens in the container, so deployment might take 5-10 minutes on first run.

To pre-download models:
```bash
docker exec vocal-splitter python -m spleeter download models
```

---

## Monitoring & Limits

- **Memory**: Spleeter uses ~500MB per processing job
- **Timeout**: Set to 300 seconds (5 minutes)
- **Upload limit**: 500MB (configurable)

For production, you may want to:
1. Add job queuing (Celery + Redis)
2. Implement file cleanup
3. Add authentication
4. Monitor memory usage

---

## Troubleshooting

**"Spleeter executable not found"**
- Run: `pip install spleeter`
- Check Python path: `which spleeter`

**"CORS errors in frontend"**
- Check `VITE_API_URL` environment variable
- Ensure backend CORS is properly configured

**"Upload fails on production"**
- Check disk space
- Verify file permissions on uploads/ folder
- Check request timeout settings

**"Models not downloading"**
- First deployment takes longer (model download)
- Pre-download in Dockerfile or first container run

---

## Next Steps

1. Choose a deployment platform from above
2. Follow the specific instructions for your platform
3. Push to GitHub
4. Monitor logs for any issues
5. Test file upload/processing on deployed app

Good luck! 🚀

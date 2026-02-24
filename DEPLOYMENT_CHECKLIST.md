# Pre-Deployment Checklist

## Frontend (React/Vite)

- [ ] Test build locally: `npm run build`
- [ ] Check for console errors in dev
- [ ] All images/assets are optimized
- [ ] API URLs correctly configured
- [ ] No hardcoded URLs (use `VITE_API_URL`)
- [ ] Build creates `dist/` folder
- [ ] Test with `npm run preview`

## Backend (Flask)

- [ ] All dependencies in `requirements-deploy.txt`
- [ ] `.env` file created with production values
- [ ] Tested with `gunicorn` locally
- [ ] CORS origins configured correctly
- [ ] Error handling for file uploads
- [ ] Logging configured properly
- [ ] Model path environment variable set
- [ ] Timeout settings increased (300s)

## Docker Setup

- [ ] Dockerfile builds without errors
- [ ] `docker-compose.yml` properly configured
- [ ] Volume mounts for uploads/output
- [ ] Port mappings correct
- [ ] Environment variables passed to container
- [ ] Tested locally with: `docker-compose up --build`

## Security

- [ ] No hardcoded secrets in code
- [ ] Use environment variables for sensitive data
- [ ] CORS properly restricted (if needed)
- [ ] File upload validation enabled
- [ ] Max file size limits set
- [ ] Input sanitization for filenames

## Production Readiness

- [ ] Choose deployment platform (Render, Railway, AWS, etc.)
- [ ] Create GitHub repository
- [ ] Push code to GitHub
- [ ] Set up CI/CD (GitHub Actions recommended)
- [ ] Create production `.env` file on server
- [ ] Test deployment URL
- [ ] Monitor first few uploads
- [ ] Set up error logging/monitoring

## Post-Deployment

- [ ] Test upload/download on live server
- [ ] Monitor server logs
- [ ] Check resource usage (memory, CPU)
- [ ] Set up automatic backups for output files
- [ ] Configure domain (if custom domain)
- [ ] Test on mobile devices
- [ ] Share with users

---

## Quick Deploy Commands

### Local Docker Deployment
```bash
docker-compose up --build
# Visit http://localhost:8000
```

### Build Frontend First
```bash
cd splitter
npm install
npm run build
cd ..
```

### Deploy to Render
```bash
git push origin main  # Automatic deployment if connected
```

### Local Testing Before Deploy
```bash
# Terminal 1: Start Flask
cd vocal-splitter-backend
python app.py

# Terminal 2: Start Frontend (dev)
cd splitter
npm run dev
```

---

## Environment Variables Template

Create `.env` on server with these values:

```
FLASK_ENV=production
FLASK_DEBUG=0
MAX_UPLOAD_SIZE=524288000
SPLEETER_MODEL_PATH=spleeter_models
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=output
```

---

## Estimated Deployment Time

- **Docker locally**: 5-10 minutes (first time)
- **Render/Railway**: 10-15 minutes
- **AWS EC2**: 30+ minutes (setup + deploy)

Good luck! 🚀

# 🚀 Deployment Guide - Sign Language App

Complete guide to deploy the Sign Language Communication Web App to production.

---

## 📋 Pre-Deployment Checklist

- [ ] All tests pass: `python test_model.py all`
- [ ] Model trained: `sign_language_model.h5` exists
- [ ] No hardcoded credentials in code
- [ ] Environment variables configured
- [ ] `.gitignore` created
- [ ] Dependencies frozen: `requirements.txt`
- [ ] Documentation complete

---

## 🎯 Deployment Options

### Option 1: Render (Recommended for Beginners)

Render is a modern platform that makes deployment simple.

#### Step 1: Create Render Account

1. Go to https://render.com
2. Sign up with GitHub
3. Verify email

#### Step 2: Create Procfile

Create `Procfile` in project root:

```
web: gunicorn app:app
release: python train_model.py
```

#### Step 3: Create .gitignore

Create `.gitignore`:

```
# Python
__pycache__/
*.pyc
*.pyo
venv/
env/
.Python

# Project
models/sign_language_model.h5
*.png
.env
.DS_Store

# IDE
.vscode/
.idea/
*.swp
```

#### Step 4: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: Sign Language App"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/sign-language.git
git push -u origin main
```

#### Step 5: Create Web Service on Render

1. Login to Render dashboard
2. Click "New +" → "Web Service"
3. Connect GitHub repository
4. Fill in details:
   - **Name**: sign-language-app
   - **Root Directory**: (leave empty)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt && python train_model.py`
   - **Start Command**: `gunicorn app:app`
5. Click "Create Web Service"

#### Step 6: Configure Environment

1. Go to "Environment" tab
2. Add variables:
   ```
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

#### Step 7: Monitor Deployment

- Build logs show progress
- Wait for "✓ Deployed successfully"
- Access at: `https://sign-language-app.onrender.com`

#### Cost
- Free tier: $0/month (sleeps after 15 min)
- Paid tier: $7/month (always on)

---

### Option 2: Railway

Railway is fast and straightforward.

#### Step 1: Create Railway Account

1. Go to https://railway.app
2. Sign up with GitHub

#### Step 2: Connect GitHub

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Authorize Railway to access GitHub
4. Select your sign-language repository

#### Step 3: Configure

Railway auto-detects Python and Flask.

Manually add environment variables if needed:
```
FLASK_ENV=production
FLASK_DEBUG=False
```

#### Step 4: Configure Start Command

In `railway.json`:

```json
{
  "build": {
    "builder": "heroku.buildpacks",
    "buildpacks": [
      "heroku/python"
    ]
  }
}
```

#### Step 5: Deploy

Click "Deploy"

Access at generated Railway domain.

#### Cost
- Pay as you go: ~$5-10/month for small apps
- Free tier available

---

### Option 3: Heroku (Legacy but Still Works)

⚠️ Heroku now requires paid dyno ($7+/month)

#### Step 1: Install Heroku CLI

```bash
# Windows
choco install heroku-cli

# macOS
brew install heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

#### Step 2: Create Procfile

```
web: gunicorn app:app
release: python train_model.py
```

#### Step 3: Login to Heroku

```bash
heroku login
```

#### Step 4: Create App

```bash
heroku create sign-language-app-YOURNAME
```

#### Step 5: Set Config Variables

```bash
heroku config:set FLASK_ENV=production
heroku config:set FLASK_DEBUG=False
```

#### Step 6: Deploy

```bash
git push heroku main
```

#### Step 7: View Logs

```bash
heroku logs --tail
```

---

### Option 4: Docker Deployment

Deploy using Docker for maximum portability.

#### Step 1: Create Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Expose port
EXPOSE 5000

# Train model on startup
RUN python train_model.py

# Run app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

#### Step 2: Create .dockerignore

```
__pycache__
*.pyc
venv/
.git
.env
models/sign_language_model.h5
```

#### Step 3: Build and Run

```bash
# Build
docker build -t sign-language-app .

# Run locally
docker run -p 5000:5000 sign-language-app

# Push to Docker Hub
docker tag sign-language-app YOUR_USERNAME/sign-language-app
docker push YOUR_USERNAME/sign-language-app
```

#### Step 4: Deploy to Container Service

- **Google Cloud Run**
- **AWS ECS**
- **Azure Container Instances**
- **DigitalOcean App Platform**

Example (Google Cloud Run):

```bash
gcloud run deploy sign-language-app \
    --source . \
    --platform managed \
    --region us-central1 \
    --memory 1Gi \
    --allow-unauthenticated
```

---

## 🔧 Production Configuration

### 1. Update app.py

```python
if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', 'False') == 'True'
    app.run(
        debug=debug,
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000))
    )
```

### 2. Install Gunicorn

```bash
pip install gunicorn
```

### 3. Test with Gunicorn

```bash
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
```

### 4. Update requirements.txt

```bash
pip freeze > requirements.txt
```

Include:
```
gunicorn==21.2.0
Flask==3.0.0
tensorflow==2.15.0
opencv-python==4.8.1.78
mediapipe==0.10.5
```

### 5. Configure for Production

In `app.py`:

```python
# Security
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Performance
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
CORS(app, resources={r"/api/*": {"origins": "https://yourdomain.com"}})
```

---

## 📊 Performance Optimization

### 1. Model Quantization

Convert to lighter format:

```python
# In train_model.py
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

with open('model.tflite', 'wb') as f:
    f.write(tflite_model)
```

### 2. Caching

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/history')
@cache.cached(timeout=5)
def get_history():
    ...
```

### 3. Compression

```python
from flask_compress import Compress

Compress(app)
```

### 4. CDN for Static Files

Use CloudFlare or AWS CloudFront:

```html
<link rel="stylesheet" href="https://cdn.example.com/css/style.css">
<script src="https://cdn.example.com/js/main.js"></script>
```

---

## 🔐 Security Hardening

### 1. HTTPS Only

Configure in Render/Railway automatically.

For self-hosted:
```bash
# Using Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --standalone -d yourdomain.com
```

### 2. CSRF Protection

```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# In HTML
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
```

### 3. Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/prediction')
@limiter.limit("30/minute")
def get_prediction():
    ...
```

### 4. Environment Secrets

Never commit sensitive data. Use `.env`:

```
# .env (DO NOT commit)
FLASK_SECRET_KEY=your-secret-key-here
API_KEY=your-api-key
DB_PASSWORD=your-password
```

In `app.py`:
```python
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
```

### 5. Input Validation

```python
from werkzeug.utils import secure_filename

@app.route('/api/upload', methods=['POST'])
def upload_file():
    filename = secure_filename(request.files['file'].filename)
    request.files['file'].save(filename)
```

---

## 📈 Monitoring & Logging

### 1. Setup Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@app.route('/api/prediction')
def get_prediction():
    logger.info('Prediction requested')
    ...
```

### 2. Error Tracking

Use Sentry for error tracking:

```bash
pip install sentry-sdk
```

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/project-id",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

### 3. Performance Monitoring

Use New Relic or DataDog:

```python
import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
```

---

## 🧪 Testing Before Deployment

### 1. Load Testing

```bash
pip install locust
```

Create `locustfile.py`:

```python
from locust import HttpUser, task

class SignLanguageUser(HttpUser):
    @task
    def get_prediction(self):
        self.client.get("/api/prediction")
```

Run:
```bash
locust -f locustfile.py --host=http://localhost:5000
```

### 2. Smoke Test

```bash
python -m pytest test_model.py -v
```

### 3. Integration Test

```bash
# Test all APIs
python test_model.py all

# Open browser manually and test UI
```

---

## 🚨 Troubleshooting Deployment

### Issue: Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
PORT=8000 gunicorn app:app
```

### Issue: Module Not Found

```bash
# Ensure dependencies installed
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.8+
```

### Issue: Webcam Not Working in Cloud

⚠️ Cloud servers don't have cameras. Options:

1. **Use mock data** for testing
2. **Stream from local** machine to cloud
3. **Accept video uploads** instead
4. **Use pre-recorded videos** for demo

### Issue: Model Too Large

If deployment fails due to size:

```bash
# Check model size
ls -lh models/sign_language_model.h5

# Train on smaller dataset
# Or quantize model to TFLite format
```

---

## 📞 Post-Deployment

### 1. Monitor Uptime

- Render: Built-in monitoring
- Railway: Built-in monitoring
- Self-hosted: Use Uptime Robot

### 2. Check Logs

```bash
# Render
render logs

# Railway
railway logs

# Heroku
heroku logs --tail

# Docker
docker logs container_name
```

### 3. Update Dependencies

```bash
# Check for updates
pip list --outdated

# Update safely
pip install --upgrade package-name

# Update all
pip install -r requirements.txt --upgrade
```

### 4. Backup Data

If using database, setup automatic backups.

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid Tier | Features |
|----------|-----------|-----------|----------|
| **Render** | Yes (sleeps) | $7/month | Simple, reliable |
| **Railway** | Partial | $5-15/month | Pay-as-you-go |
| **Heroku** | No | $7/month | Popular, mature |
| **Vercel** | Yes | $20/month | For frontend |
| **Docker** | Self-hosted | Server cost | Maximum control |

---

## 🎓 Learning Paths

**Beginner** → Deploy to Render  
**Intermediate** → Deploy with Railway  
**Advanced** → Docker + custom server  
**Expert** → Kubernetes cluster  

---

## 📚 Additional Resources

- [Render Docs](https://render.com/docs)
- [Railway Docs](https://railway.app/docs)
- [Flask Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Gunicorn Guide](https://gunicorn.org/)
- [Docker For Beginners](https://docs.docker.com/get-started/)

---

## ✅ Post-Deployment Checklist

- [ ] App loads successfully
- [ ] Webcam stream works
- [ ] Predictions display correctly
- [ ] Text builder functional
- [ ] All buttons work
- [ ] Error handling working
- [ ] Logs look clean
- [ ] No error messages
- [ ] Performance acceptable
- [ ] HTTPS enabled (if applicable)
- [ ] Monitoring configured
- [ ] Backups setup (if needed)

---

Deployment complete! 🎉

For production support, consider a managed service like Render for simplicity or Docker for control.

# 🚀 Python/Flask Deployment Guide for Dokploy VPS

## 📚 Complete Guide for Deploying Python Flask Applications on Dokploy with Nixpacks

**Last Updated:** August 25, 2025  
**Tested With:** Flask 2.3.3, Gunicorn 21.2.0, Dokploy with Nixpacks

---

## 📋 Table of Contents

1. [Quick Start Checklist](#quick-start-checklist)
2. [Project Structure](#project-structure)
3. [Code Configuration](#code-configuration)
4. [Dokploy Configuration](#dokploy-configuration)
5. [Deployment Steps](#deployment-steps)
6. [Troubleshooting](#troubleshooting)
7. [Key Lessons Learned](#key-lessons-learned)

---

## 🎯 Quick Start Checklist

### ✅ Project Files Needed:
- [ ] `app.py` - Main Flask application
- [ ] `wsgi.py` - Gunicorn entry point
- [ ] `requirements.txt` - Python dependencies
- [ ] `nixpacks.toml` - Nixpacks configuration (optional)
- [ ] `Procfile` - For compatibility (optional)
- [ ] `/templates/` - HTML templates
- [ ] `/static/` - CSS, JS, images

### ✅ Dokploy Settings:
- [ ] Build Type: `Nixpacks`
- [ ] Environment Variables configured
- [ ] Domain with Container Port set
- [ ] GitHub repository connected

---

## 📁 Project Structure

### Minimum Required Structure:
```
your-flask-app/
├── app.py              # Main Flask application
├── wsgi.py             # Gunicorn entry point
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   └── index.html
└── static/             # Static files
    ├── style.css
    └── script.js
```

### Optional Files:
```
├── nixpacks.toml       # Override Nixpacks defaults
├── Procfile            # For Heroku compatibility
├── .env                # Local environment variables
└── README.md           # Documentation
```

---

## 💻 Code Configuration

### 1. **app.py** - Main Flask Application
```python
from flask import Flask, render_template, request, jsonify, send_file
import os
import tempfile
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    # Your application logic here
    return jsonify({'success': True})

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(404)
def not_found(e):
    return render_template('index.html')

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # This block is for local development only
    # Gunicorn ignores this in production
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
```

### 2. **wsgi.py** - Gunicorn Entry Point (CRITICAL!)
```python
from app import app

if __name__ == "__main__":
    app.run()
```

**⚠️ IMPORTANT:** This file is mandatory for Gunicorn deployment!

### 3. **requirements.txt** - Dependencies
```txt
Flask==2.3.3
gunicorn==21.2.0
Werkzeug==2.3.7
# Add other dependencies as needed
```

### 4. **nixpacks.toml** (Optional - NOT recommended for Dokploy)
```toml
[variables]
PYTHON_VERSION = "3.11"

[start]
# DON'T use $PORT with Dokploy - it won't be injected!
cmd = "gunicorn -b 0.0.0.0:8000 --workers 2 wsgi:app"
```

**⚠️ NOTE:** Better to set this via Environment Variables in Dokploy instead!

### 5. **Procfile** (Optional - for other platforms)
```
web: gunicorn -b 0.0.0.0:$PORT --workers 2 wsgi:app
```

---

## ⚙️ Dokploy Configuration

### 1. Create New Application

1. **Applications** → **Create Application**
2. Select **GitHub** as Provider
3. Choose your repository
4. Select **main** branch

### 2. Build Configuration

| Setting | Value |
|---------|--------|
| **Build Type** | `Nixpacks` |
| **Build Path** | `/` (root of repo) |
| **Trigger Type** | `On Push` |
| **Watch Paths** | Leave empty for all files |

### 3. Environment Variables (CRITICAL!)

Go to **Environment** tab and add:

```bash
# CRITICAL - Fixed port instead of $PORT variable!
NIXPACKS_START_CMD=gunicorn --bind 0.0.0.0:8000 --workers 2 wsgi:app

# Python version specification
NIXPACKS_PYTHON_VERSION=3.11

# Optional - if you have other environment needs
# DATABASE_URL=your_database_url
# SECRET_KEY=your_secret_key
```

**⚠️ CRITICAL NOTES:**
- **DO NOT use `$PORT`** - Dokploy doesn't inject it!
- **Use fixed port `8000`** in the start command
- **Match this port in Domain settings**

### 4. Domain Configuration

1. Go to **Domains** tab
2. Click **Create Domain**
3. Configure:

| Setting | Value |
|---------|--------|
| **Host** | `your-app.domain.com` |
| **Container Port** | `8000` (MUST match start command!) |
| **Path** | `/` |
| **Certificate** | `Let's Encrypt` |
| **Email** | Your email for SSL |

**⚠️ CRITICAL:** Container Port MUST match the port in `NIXPACKS_START_CMD`!

### 5. Advanced Settings (Optional)

| Setting | Recommended Value |
|---------|------------------|
| **Memory** | `512` MB minimum |
| **CPU** | `500` millicores |
| **Replicas** | `1` for start |
| **Health Check Path** | `/` or `/health` |
| **Health Check Interval** | `30` seconds |

---

## 🚀 Deployment Steps

### Step 1: Prepare Your Code

1. Ensure all required files are in your repository
2. Test locally:
   ```bash
   pip install -r requirements.txt
   gunicorn --bind 0.0.0.0:8000 --workers 2 wsgi:app
   ```
3. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Ready for Dokploy deployment"
   git push origin main
   ```

### Step 2: Configure DNS

1. Add A record pointing to your VPS IP:
   ```
   Type: A
   Name: your-subdomain
   Value: [VPS-IP]
   TTL: 3600
   ```
2. Wait for DNS propagation (5-30 minutes)

### Step 3: Deploy in Dokploy

1. Click **Deploy** button
2. Monitor **Logs** tab for progress
3. Look for successful messages:
   ```
   ✅ Docker Deployed
   Listening at: http://0.0.0.0:8000
   ```

### Step 4: Verify Deployment

1. Check application logs for errors
2. Access your domain: `https://your-app.domain.com`
3. Test functionality

---

## 🔧 Troubleshooting

### Problem: "Bad Gateway" Error

**Symptoms:**
- Deploy succeeds but site shows "Bad Gateway"
- Error in logs: `Error: '' is not a valid port number`

**Solution:**
```bash
# In Environment Variables, change from:
NIXPACKS_START_CMD=gunicorn -b 0.0.0.0:$PORT --workers 2 wsgi:app

# To fixed port:
NIXPACKS_START_CMD=gunicorn --bind 0.0.0.0:8000 --workers 2 wsgi:app
```

**Root Cause:** Dokploy doesn't inject `$PORT` variable like Heroku/Railway

---

### Problem: "403 Forbidden" on ghcr.io/railwayapp/nixpacks

**Symptoms:**
- Build fails with Docker registry authentication error
- `failed to fetch oauth token: 403 Forbidden`

**Solution:**
1. Create GitHub Personal Access Token with `read:packages` scope
2. In Dokploy: **Settings** → **Registries** → **New Registry**
3. Configure:
   - Registry Name: `GHCR`
   - Username: Your GitHub username
   - Password: Your GitHub PAT
   - Registry URL: `ghcr.io`

---

### Problem: Module Not Found

**Symptoms:**
- Import errors in production
- Modules work locally but not on deployment

**Solution:**
1. Ensure all dependencies are in `requirements.txt`
2. Check Python version compatibility:
   ```bash
   NIXPACKS_PYTHON_VERSION=3.11  # Match your local version
   ```

---

### Problem: Static Files Not Serving

**Symptoms:**
- CSS/JS files return 404
- Images don't load

**Solution:**
1. Ensure Flask is configured for static files:
   ```python
   app = Flask(__name__, 
               static_folder='static',
               static_url_path='/static')
   ```
2. Use `url_for` in templates:
   ```html
   <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
   ```

---

## 💡 Key Lessons Learned

### 1. **Port Configuration**
- ❌ **DON'T** rely on `$PORT` environment variable
- ✅ **DO** use fixed port (e.g., 8000) in both start command and domain settings
- ✅ **DO** ensure Container Port matches the actual port Gunicorn binds to

### 2. **Environment Variables**
- Use `NIXPACKS_START_CMD` to override default start command
- Use `NIXPACKS_PYTHON_VERSION` to specify Python version
- All custom env vars should be added in Dokploy's Environment tab

### 3. **File Structure**
- `wsgi.py` is mandatory for Gunicorn
- Keep requirements minimal and specific
- Don't rely on nixpacks.toml - use Environment Variables instead

### 4. **Debugging**
- Always check **Logs** tab in Dokploy
- Look for "Listening at" message to confirm port
- Verify Container Port matches actual listening port

---

## 📝 Quick Reference

### Minimal Environment Variables for Dokploy:
```bash
NIXPACKS_START_CMD=gunicorn --bind 0.0.0.0:8000 --workers 2 wsgi:app
NIXPACKS_PYTHON_VERSION=3.11
```

### Domain Settings:
- **Container Port:** `8000` (must match start command)
- **Host:** Your subdomain
- **Path:** `/`

### Common Ports:
- `8000` - Standard Python/Django/Flask port
- `5000` - Flask development default (avoid in production)
- `3000` - Node.js default (don't use for Python)

---

## 🆘 Support Notes

### When Things Go Wrong:
1. **Check Logs** - Most issues are visible in deployment/runtime logs
2. **Verify Ports** - Ensure start command port matches Container Port
3. **Test Locally** - Run Gunicorn locally with same command
4. **DNS Check** - Ensure domain points to correct IP
5. **SSL Issues** - Wait for Let's Encrypt or check DNS

### Success Indicators:
- ✅ "Docker Deployed: ✅" in build logs
- ✅ "Listening at: http://0.0.0.0:8000" in runtime logs
- ✅ Site accessible via HTTPS
- ✅ No "Bad Gateway" errors

---

## 📚 Additional Resources

- [Dokploy Documentation](https://docs.dokploy.com)
- [Nixpacks Python Provider](https://nixpacks.up.railway.app/docs/providers/python)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/configure.html)
- [Flask Deployment Options](https://flask.palletsprojects.com/en/2.3.x/deploying/)

---

**Created:** August 25, 2025  
**Based on:** Real deployment experience with VTT Transcript Cleaner on Dokploy VPS  
**Status:** ✅ Tested and Working

---

## 🎯 TL;DR - Quick Deploy

1. **Code:** Create `app.py`, `wsgi.py`, `requirements.txt`
2. **Dokploy Environment:**
   ```
   NIXPACKS_START_CMD=gunicorn --bind 0.0.0.0:8000 --workers 2 wsgi:app
   NIXPACKS_PYTHON_VERSION=3.11
   ```
3. **Domain:** Set Container Port to `8000`
4. **Deploy:** Push to GitHub → Auto-deploy
5. **Done!** 🚀

---

## 📖 Appendix: Understanding the Components

### 🔍 Why Gunicorn?

**The Problem with Flask's Built-in Server:**
```python
app.run()  # ⚠️ NEVER use in production!
```
- **Single-threaded** - processes only 1 request at a time
- **Not secure** - debug mode exposes source code
- **Not stable** - crashes easily under load
- **Flask documentation clearly states:** "Do not use the development server in production"

**What is Gunicorn?**

Gunicorn (Green Unicorn) is a Python WSGI HTTP Server that acts as a bridge between web requests and your Flask application:

```
Browser → Nginx/Traefik → Gunicorn → Flask App
                          ↓
                    [Multiple Workers]
```

**Key Benefits:**
- **Multi-worker processing** - handles multiple requests simultaneously
- **Process management** - automatic restart on crashes
- **Load balancing** - distributes requests across workers
- **Production-ready** - battle-tested by Instagram, Pinterest, etc.

**Popular Alternatives:**

| Server | Use Case | Command Example |
|--------|----------|-----------------|
| **Gunicorn** | Standard for Flask/Django | `gunicorn --bind 0.0.0.0:8000 wsgi:app` |
| **uWSGI** | Complex enterprise apps | `uwsgi --http :8000 --module wsgi:app` |
| **Waitress** | Windows environments | `waitress-serve --port=8000 wsgi:app` |
| **Uvicorn** | Async apps (FastAPI) | `uvicorn app:app --host 0.0.0.0` |

**Industry Standard:** ~70% of Flask/Django deployments use Gunicorn

---

### 📄 Why nixpacks.toml and Procfile are Optional

**nixpacks.toml:**
- **Purpose:** Configuration file for Nixpacks build system
- **Optional because:** Dokploy allows setting all configurations via Environment Variables
- **When it's required:** 
  - On Railway/Render platforms
  - For complex build steps
  - In monorepo setups
- **Why we keep it:** Documentation and portability

**Procfile:**
- **Purpose:** Heroku's deployment configuration format
- **Optional because:** Dokploy uses Nixpacks, not Heroku buildpacks
- **When it's required:**
  - Deploying to Heroku (mandatory!)
  - Deploying to Dokku or similar
  - DigitalOcean App Platform
- **Why we keep it:** Platform flexibility and fallback

**Configuration Precedence in Dokploy:**
1. **Environment Variables** (NIXPACKS_START_CMD) - Highest priority
2. **nixpacks.toml** - If no env var exists
3. **Procfile** - If neither above exists
4. **Auto-detect** - Nixpacks guesses (often incorrectly)

**Best Practice:**
- Use Environment Variables in Dokploy for flexibility
- Keep configuration files in code for documentation and portability
- No harm in having both - they're just small text files

---

**End of Guide** 📚
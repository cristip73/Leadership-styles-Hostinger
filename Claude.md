# Migration Plan: Streamlit/PostgreSQL → Flask/SQLite for Dokploy

## 🎯 Migration Strategy

### Major Conversions Required
1. **Framework**: Streamlit → Flask + Gunicorn
2. **Database**: PostgreSQL → SQLite
3. **Deployment**: Following exact PYTHON_FLASK_DOKPLOY_DEPLOYMENT_GUIDE.md

## Current State Analysis

### Current Application (Streamlit)
```
Leadership-styles-Hostinger/
├── main.py                    # Streamlit entry
├── pages/                     # Multipage Streamlit
│   ├── 01_take_assessment.py # Assessment form
│   ├── 02_view_results.py    # Results display
│   └── 03_supervisor.py      # Admin panel
├── models/
│   └── database.py           # PostgreSQL connection
├── utils/
│   ├── auth.py              # Authentication
│   ├── scoring.py           # Assessment scoring
│   └── visualization.py     # Plotly charts
├── assets/
│   └── test_data.py         # Questions data
└── .streamlit/
    └── config.toml          # Streamlit config
```

### Current Features
- User registration form
- 12-question assessment
- Management style calculation
- Adequacy scoring
- Results visualization (Plotly)
- Supervisor dashboard
- Excel/CSV export

## Target Flask Application Structure

### New File Structure (Flask)
```
Leadership-styles-Hostinger/
├── app.py                    # Main Flask application
├── wsgi.py                   # Gunicorn entry point (CRITICAL!)
├── requirements.txt          # Python dependencies
├── database.py               # SQLite connection
├── templates/                # HTML templates
│   ├── base.html            # Base template
│   ├── index.html           # Home page
│   ├── assessment.html      # Assessment form
│   ├── results.html         # Results display
│   └── supervisor.html      # Admin panel
├── static/                   # Static files
│   ├── css/
│   │   └── style.css       # Custom styles
│   └── js/
│       └── app.js          # JavaScript logic
├── utils/
│   ├── auth.py              # Keep existing
│   ├── scoring.py           # Keep existing
│   └── visualization.py     # Modify for Flask
├── assets/
│   └── test_data.py         # Keep existing
└── instance/
    └── assessment.db        # SQLite database (auto-created)
```

## Conversion Tasks

### Phase 1: Database Migration (PostgreSQL → SQLite)

#### New database.py for SQLite
```python
import sqlite3
import uuid
import json
from datetime import datetime

class Database:
    def __init__(self, db_path='instance/assessment.db'):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        conn = self.get_connection()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                question_id INTEGER,
                answer TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                primary_style TEXT,
                secondary_style TEXT,
                adequacy_score INTEGER,
                adequacy_level TEXT,
                directiv_score INTEGER,
                persuasiv_score INTEGER,
                participativ_score INTEGER,
                delegativ_score INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()
        conn.close()
```

### Phase 2: Flask Application Structure

#### app.py (Main Flask Application)
```python
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
from database import Database
from utils.scoring import AssessmentScorer
from utils.auth import check_supervisor_password
from assets.test_data import QUESTIONS
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db = Database()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/assessment', methods=['GET', 'POST'])
def assessment():
    if request.method == 'POST':
        # Handle form submission
        data = request.json
        # Process assessment logic
        return jsonify({'success': True})
    return render_template('assessment.html', questions=QUESTIONS)

@app.route('/results/<user_id>')
def results(user_id):
    # Get results from database
    return render_template('results.html', user_id=user_id)

@app.route('/supervisor', methods=['GET', 'POST'])
def supervisor():
    # Admin panel logic
    return render_template('supervisor.html')

# API endpoints for AJAX
@app.route('/api/submit_assessment', methods=['POST'])
def submit_assessment():
    # Handle assessment submission
    return jsonify({'success': True})

@app.route('/api/export/<format>')
def export_data(format):
    # Export to Excel/CSV
    return send_file(...)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
```

#### wsgi.py (CRITICAL for Gunicorn!)
```python
from app import app

if __name__ == "__main__":
    app.run()
```

### Phase 3: UI Conversion (Streamlit → HTML/JavaScript)

#### Key UI Components to Convert
1. **st.form** → HTML `<form>` with JavaScript validation
2. **st.button** → HTML `<button>` with event handlers
3. **st.selectbox/radio** → HTML `<select>/<input type="radio">`
4. **st.progress** → Bootstrap progress bar
5. **Plotly charts** → Plotly.js in browser
6. **st.session_state** → Flask session or JavaScript localStorage
7. **st.tabs** → Bootstrap tabs
8. **st.dataframe** → HTML table or DataTables.js

### Phase 4: Files for Dokploy Deployment

#### requirements.txt
```txt
Flask==2.3.3
gunicorn==21.2.0
Werkzeug==2.3.7
pandas==2.2.3
plotly==5.24.1
bcrypt==4.2.0
openpyxl==3.1.5
xlsxwriter==3.2.0
```

#### Procfile (Optional)
```
web: gunicorn -b 0.0.0.0:$PORT --workers 2 wsgi:app
```

#### nixpacks.toml (Optional)
```toml
[variables]
PYTHON_VERSION = "3.11"

[start]
cmd = "gunicorn -b 0.0.0.0:8000 --workers 2 wsgi:app"
```

## Dokploy Configuration

### Environment Variables
```bash
# CRITICAL - Fixed port, no $PORT variable!
NIXPACKS_START_CMD=gunicorn --bind 0.0.0.0:8000 --workers 2 wsgi:app

# Python version
NIXPACKS_PYTHON_VERSION=3.11

# Application secrets
SECRET_KEY=your-secret-key-here
SUPERVISOR_PASSWORD=your-admin-password
```

### Domain Settings
| Setting | Value |
|---------|--------|
| **Container Port** | `8000` |
| **Host** | `your-domain.com` |
| **Path** | `/` |

## Implementation Steps

### Step 1: Core Conversion (Priority)
1. ⏳ Create `app.py` with Flask routes
2. ⏳ Create `wsgi.py` (mandatory!)
3. ⏳ Convert `database.py` to SQLite
4. ⏳ Create `requirements.txt`

### Step 2: Template Creation
1. ⏳ Create `templates/base.html` (Bootstrap 5)
2. ⏳ Convert assessment logic to `templates/assessment.html`
3. ⏳ Convert results display to `templates/results.html`
4. ⏳ Convert supervisor panel to `templates/supervisor.html`

### Step 3: Static Assets
1. ⏳ Create `static/css/style.css`
2. ⏳ Create `static/js/app.js` for interactive features
3. ⏳ Integrate Plotly.js for charts

### Step 4: Feature Migration
1. ⏳ User registration flow
2. ⏳ Assessment question navigation
3. ⏳ Response storage
4. ⏳ Score calculation
5. ⏳ Results visualization
6. ⏳ Export functionality

### Step 5: Cleanup
1. ⏳ Remove Streamlit files (`main.py`, `pages/`)
2. ⏳ Remove `.streamlit/` folder
3. ⏳ Remove Replit files (`.replit`, `replit.nix`)
4. ⏳ Remove `pyproject.toml`, `uv.lock`
5. ⏳ Clean up `Pasted-*.txt` files

### Step 6: Testing
1. ⏳ Test locally with Flask development server
2. ⏳ Test with Gunicorn locally
3. ⏳ Verify SQLite database operations
4. ⏳ Test all features end-to-end

### Step 7: Deployment
1. ⏳ Push to GitHub
2. ⏳ Configure Dokploy
3. ⏳ Deploy and monitor logs
4. ⏳ Test production deployment

## Critical Considerations

### Session Management
- Flask sessions for user state (replacing st.session_state)
- Consider Flask-Session for production
- UUID generation for user tracking

### Database Migration
- SQLite file will be in `instance/` folder
- Ensure proper file permissions
- Consider backup strategy

### UI/UX Changes
- Bootstrap 5 for responsive design
- JavaScript for interactivity
- AJAX for seamless updates
- Progress indication during assessment

### Security
- CSRF protection for forms
- Input validation
- SQL injection prevention (use parameterized queries)
- XSS prevention (use Jinja2 auto-escaping)

## Testing Commands

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Run Flask development server
python app.py

# Test with Gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 2 wsgi:app
```

## Advantages of This Migration

1. **Simpler Deployment**: Flask/Gunicorn is standard, well-documented
2. **No External Database**: SQLite is file-based, no setup needed
3. **Better Performance**: Flask is lighter than Streamlit
4. **More Control**: Full control over UI/UX
5. **Standard Stack**: Flask/Gunicorn/SQLite is industry standard

## Challenges to Address

1. **UI Recreation**: Need to rebuild entire UI in HTML/CSS/JS
2. **Interactivity**: JavaScript needed for dynamic features
3. **Chart Integration**: Plotly.js setup in browser
4. **Session Management**: Different from Streamlit's approach
5. **File Uploads**: If needed, handle differently in Flask

## Next Actions

1. **Immediate**: Start with core Flask structure (`app.py`, `wsgi.py`)
2. **Priority**: Database migration to SQLite
3. **Then**: Template creation for each page
4. **Finally**: JavaScript for interactivity and charts

This is a significant rewrite but will result in a more standard, deployable application that follows the Dokploy guide exactly.
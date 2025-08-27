from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
import os
import uuid
import json
from datetime import datetime
import io
import pandas as pd

from database import Database
from utils.scoring import AssessmentScorer
from utils.auth import check_supervisor_password
from assets.test_data import QUESTIONS

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Initialize database
db = Database()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/assessment')
def assessment():
    # Clear any previous assessment data
    session['current_question'] = 0
    session['responses'] = {}
    session['user_id'] = None
    return render_template('assessment.html', questions=QUESTIONS)

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user for assessment"""
    try:
        data = request.json
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        email = data.get('email', '').strip()
        
        if not all([first_name, last_name, email]):
            return jsonify({'success': False, 'error': 'All fields are required'}), 400
        
        # Create user
        user_id = db.create_user(first_name, last_name, email)
        
        # Clear and reinitialize session
        session.clear()
        session['user_id'] = str(user_id)
        session['responses'] = {}
        session['current_question'] = 1
        session.permanent = True  # Make session permanent
        session.modified = True  # Force session to save
        
        print(f"DEBUG: User registered: {user_id}")
        print(f"DEBUG: Session initialized with user_id: {session.get('user_id')}")
        
        return jsonify({'success': True, 'user_id': str(user_id)})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': 'Registration failed'}), 500

@app.route('/api/submit_answer', methods=['POST'])
def submit_answer():
    """Submit answer for current question"""
    try:
        print(f"DEBUG: Session at start - User: {session.get('user_id')}, Responses: {session.get('responses', {})}")
        
        if 'user_id' not in session:
            print("DEBUG: No user_id in session!")
            return jsonify({'success': False, 'error': 'Not registered'}), 401
        
        data = request.json
        question_id = data.get('question_id')
        answer = data.get('answer', '').upper()
        
        print(f"DEBUG: Received Q{question_id}: {answer}")
        
        if not answer or answer not in ['A', 'B', 'C', 'D']:
            return jsonify({'success': False, 'error': 'Invalid answer'}), 400
        
        # Save response to session
        if 'responses' not in session:
            print("DEBUG: Creating new responses dict in session")
            session['responses'] = {}
        session['responses'][str(question_id)] = answer
        
        # Force session to save
        session.modified = True
        
        print(f"DEBUG: Session responses count: {len(session['responses'])}")
        print(f"DEBUG: Session contains: {list(session['responses'].keys())}")
        print(f"DEBUG: Total questions: {len(QUESTIONS)}")
        
        # Save to database
        db.save_response(session['user_id'], question_id, answer)
        
        # Check if all questions answered
        if len(session['responses']) >= len(QUESTIONS):
            print("DEBUG: All questions answered, calculating results...")
            # Calculate results
            scorer = AssessmentScorer()
            responses_dict = {int(k): v for k, v in session['responses'].items()}
            
            print(f"DEBUG: Responses dict: {responses_dict}")
            
            # Get style scores
            primary_style, secondary_style = scorer.calculate_style_scores(responses_dict)
            adequacy_score, adequacy_tier = scorer.calculate_adequacy_score(responses_dict)
            
            print(f"DEBUG: Primary: {primary_style}, Secondary: {secondary_style}")
            print(f"DEBUG: Adequacy: {adequacy_score}, Level: {adequacy_tier}")
            
            # Get all style scores
            style_scores = scorer.get_all_style_scores([{'question_id': k, 'answer': v} 
                                                        for k, v in responses_dict.items()])
            
            print(f"DEBUG: Style scores: {style_scores}")
            
            # Save results
            db.save_results(
                session['user_id'],
                primary_style,
                secondary_style,
                adequacy_score,
                adequacy_tier,
                style_scores
            )
            
            print(f"DEBUG: Results saved! User ID: {session['user_id']}")
            
            return jsonify({
                'success': True,
                'completed': True,
                'user_id': session['user_id']
            })
        
        return jsonify({'success': True, 'completed': False})
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/results/<user_id>')
def results(user_id):
    """Display results for a user"""
    try:
        result = db.get_user_results(user_id)
        if not result:
            return redirect(url_for('index'))
        
        # Create chart data for Plotly
        style_data = {
            'labels': ['Directiv', 'Persuasiv', 'Participativ', 'Delegativ'],
            'values': [
                result['directiv_score'],
                result['persuasiv_score'],
                result['participativ_score'],
                result['delegativ_score']
            ]
        }
        
        return render_template('results.html', 
                             result=result,
                             style_data=json.dumps(style_data))
    except Exception as e:
        return redirect(url_for('index'))

@app.route('/supervisor')
def supervisor():
    """Supervisor dashboard"""
    if not session.get('supervisor_authenticated'):
        return render_template('supervisor_login.html')
    
    results = db.get_all_results()
    return render_template('supervisor.html', results=results)

@app.route('/api/supervisor_login', methods=['POST'])
def supervisor_login():
    """Authenticate supervisor"""
    try:
        data = request.json
        password = data.get('password', '')
        
        if check_supervisor_password(password):
            session['supervisor_authenticated'] = True
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': 'Invalid password'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/compare', methods=['POST'])
def compare_profiles():
    """Compare multiple user profiles"""
    if not session.get('supervisor_authenticated'):
        return jsonify({'error': 'Not authorized'}), 401
    
    try:
        data = request.json
        user_ids = data.get('user_ids', [])
        
        if len(user_ids) < 2 or len(user_ids) > 4:
            return jsonify({'error': 'Please select 2-4 participants'}), 400
        
        comparison_data = []
        for user_id in user_ids:
            result = db.get_user_results(user_id)
            if result:
                comparison_data.append({
                    'id': result['user_id'],
                    'name': f"{result['first_name']} {result['last_name']}",
                    'email': result['email'],
                    'primary_style': result['primary_style'],
                    'secondary_style': result['secondary_style'],
                    'directiv_score': result['directiv_score'] or 0,
                    'persuasiv_score': result['persuasiv_score'] or 0,
                    'participativ_score': result['participativ_score'] or 0,
                    'delegativ_score': result['delegativ_score'] or 0,
                    'adequacy_score': result['adequacy_score'] or 0,
                    'adequacy_level': result['adequacy_level']
                })
        
        return jsonify({'success': True, 'data': comparison_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/<format>')
def export_data(format):
    """Export results to Excel or CSV"""
    if not session.get('supervisor_authenticated'):
        return jsonify({'error': 'Not authorized'}), 401
    
    try:
        results = db.get_all_results()
        
        # Convert to DataFrame
        df = pd.DataFrame(results)
        
        # Select relevant columns
        columns = ['first_name', 'last_name', 'email', 'primary_style', 
                  'secondary_style', 'adequacy_score', 'adequacy_level',
                  'directiv_score', 'persuasiv_score', 'participativ_score', 
                  'delegativ_score', 'created_at']
        
        df = df[columns]
        
        # Create file in memory
        output = io.BytesIO()
        
        if format == 'excel':
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Results', index=False)
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'assessment_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            )
        
        elif format == 'csv':
            df.to_csv(output, index=False)
            output.seek(0)
            
            return send_file(
                output,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'assessment_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            )
        
        return jsonify({'error': 'Invalid format'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    """Clear session"""
    session.clear()
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
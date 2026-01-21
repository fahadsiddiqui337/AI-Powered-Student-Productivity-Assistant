"""
AI-Powered Student Productivity Assistant
Combines Machine Learning + Claude AI for personalized study help!
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
#from ml_model import StudentProductivityML, get_study_advice
import os

# Initialize Flask app
app = Flask(__name__)

# Initialize the ML model
#ml_model = StudentProductivityML()

# Store study sessions in memory (in real app, use a database)
study_sessions = []
student_profile = {
    'name': 'Student',
    'total_study_time': 0,
    'total_sessions': 0,
    'average_focus': 5.0
}


# ============== MAIN PAGE ==============
@app.route('/')
def index():
    """
    Main dashboard - shows everything at a glance
    """
    return render_template('index.html', 
                         profile=student_profile,
                         sessions=study_sessions[-5:])  # Show last 5 sessions


# ============== START STUDY SESSION ==============
@app.route('/start-session', methods=['POST'])
def start_session():
    """
    Start a new study session with ML predictions
    """
    data = request.get_json()
    
    # Get current time information
    now = datetime.now()
    hour = now.hour
    day_of_week = now.weekday()  # 0 = Monday, 6 = Sunday
    
    # Get user inputs
    subject = data.get('subject', 'General Study')
    planned_duration = int(data.get('duration', 25))
    
    # ML PREDICTION: How focused will they be?
    predicted_focus = ml_model.predict_focus_score(
        hour=hour,
        day_of_week=day_of_week,
        duration=planned_duration,
        breaks=0
    )
    
    # Get personalized recommendations
    break_advice = ml_model.get_break_recommendation(0)
    
    session = {
        'id': len(study_sessions) + 1,
        'subject': subject,
        'start_time': now.strftime('%Y-%m-%d %H:%M:%S'),
        'hour': hour,
        'day_of_week': day_of_week,
        'planned_duration': planned_duration,
        'predicted_focus': round(predicted_focus, 1),
        'status': 'active',
        'breaks_taken': 0
    }
    
    study_sessions.append(session)
    
    return jsonify({
        'success': True,
        'session': session,
        'advice': break_advice,
        'ml_insight': f"ML predicts focus score: {round(predicted_focus, 1)}/10"
    })


# ============== END STUDY SESSION ==============
@app.route('/end-session', methods=['POST'])
def end_session():
    """
    End study session and record actual performance
    """
    data = request.get_json()
    
    session_id = data.get('session_id')
    actual_duration = int(data.get('actual_duration', 25))
    focus_score = int(data.get('focus_score', 5))
    breaks_taken = int(data.get('breaks', 0))
    
    # Find and update the session
    for session in study_sessions:
        if session['id'] == session_id:
            session['status'] = 'completed'
            session['duration'] = actual_duration
            session['focus_score'] = focus_score
            session['breaks'] = breaks_taken
            session['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Update student profile
            student_profile['total_study_time'] += actual_duration
            student_profile['total_sessions'] += 1
            
            # Calculate new average focus
            completed = [s for s in study_sessions if s.get('status') == 'completed']
            if completed:
                avg = sum(s.get('focus_score', 5) for s in completed) / len(completed)
                student_profile['average_focus'] = round(avg, 1)
            
            break
    
    # RETRAIN ML MODEL with new data
    completed_sessions = [s for s in study_sessions if s.get('status') == 'completed']
    if len(completed_sessions) >= 3:
        ml_model.train(completed_sessions)
    
    return jsonify({
        'success': True,
        'message': 'Session saved! ML model updated with your data '
    })


# ============== GET ML INSIGHTS ==============
@app.route('/get-insights', methods=['GET'])
def get_insights():
    """
    Get personalized insights from ML analysis
    """
    completed = [s for s in study_sessions if s.get('status') == 'completed']
    
    if len(completed) < 3:
        return jsonify({
            'ready': False,
            'message': 'Complete 3+ study sessions to unlock AI insights!'
        })
    
    # Train model if needed
    if not ml_model.is_trained:
        ml_model.train(completed)
    
    # Get ML recommendations
    best_time = ml_model.get_best_study_time(completed)
    optimal_duration = ml_model.calculate_optimal_duration(completed)
    trend = ml_model.analyze_performance_trend(completed)
    
    # Get study advice
    advice = get_study_advice(student_profile)
    
    insights = {
        'ready': True,
        'best_study_time': f"{best_time['best_hour_formatted']} on {best_time['best_day']}s",
        'optimal_duration': f"{optimal_duration} minutes",
        'performance_trend': trend['message'],
        'advice': advice,
        'total_sessions': len(completed),
        'average_focus': student_profile['average_focus'],
        'total_hours': round(student_profile['total_study_time'] / 60, 1)
    }
    
    return jsonify(insights)


# ============== PREDICT FOCUS FOR CUSTOM TIME ==============
@app.route('/predict-focus', methods=['POST'])
def predict_focus():
    """
    Predict focus score for a specific time/day
    """
    data = request.get_json()
    
    hour = int(data.get('hour', 14))
    day = int(data.get('day', 1))
    duration = int(data.get('duration', 25))
    
    completed = [s for s in study_sessions if s.get('status') == 'completed']
    
    if len(completed) >= 3 and not ml_model.is_trained:
        ml_model.train(completed)
    
    prediction = ml_model.predict_focus_score(hour, day, duration, 0)
    
    # Interpret the prediction
    if prediction >= 8:
        interpretation = "Excellent time to study! "
    elif prediction >= 6:
        interpretation = "Good time for studying "
    elif prediction >= 4:
        interpretation = "Okay time, but not your best "
    else:
        interpretation = "Consider a different time "
    
    return jsonify({
        'predicted_focus': round(prediction, 1),
        'interpretation': interpretation,
        'confidence': 'high' if len(completed) >= 10 else 'medium'
    })


# ============== GET AI STUDY TIPS (uses simple logic) ==============
@app.route('/get-ai-tips', methods=['POST'])
def get_ai_tips():
    """
    Generate personalized AI study tips based on performance
    """
    data = request.get_json()
    subject = data.get('subject', 'general')
    difficulty = data.get('difficulty', 'medium')
    
    # Simple AI logic (you can enhance this!)
    tips = []
    
    if difficulty == 'hard':
        tips = [
            " Break it into smaller topics and master one at a time",
            " Use active recall: Test yourself instead of re-reading",
            " Find a study buddy or join a study group",
            " Watch explanation videos for visual learning"
        ]
    elif difficulty == 'medium':
        tips = [
            " Use spaced repetition: Review material over several days",
            " Create mind maps to connect concepts",
            " Study in focused 25-minute sessions (Pomodoro)",
            " Teach the material to someone else"
        ]
    else:
        tips = [
            " Quick review sessions work great!",
            " Make flashcards for key concepts",
            " Focus on practice problems",
            " Quiz yourself regularly"
        ]
    
    # Add personalized tip based on ML insights
    if ml_model.is_trained:
        completed = [s for s in study_sessions if s.get('status') == 'completed']
        best_time = ml_model.get_best_study_time(completed)
        tips.append(f" Your best study time is around {best_time['best_hour_formatted']}")
    
    return jsonify({
        'tips': tips,
        'subject': subject,
        'difficulty': difficulty
    })


# ============== GET ALL SESSIONS ==============
@app.route('/get-sessions', methods=['GET'])
def get_sessions():
    """
    Return all study sessions for display
    """
    completed = [s for s in study_sessions if s.get('status') == 'completed']
    
    return jsonify({
        'sessions': completed[-10:],  # Last 10 sessions
        'total': len(completed)
    })


# ============== RESET DATA ==============
@app.route('/reset', methods=['POST'])
def reset_data():
    """
    Reset all data (useful for testing)
    """
    global study_sessions, student_profile, ml_model
    
    study_sessions = []
    student_profile = {
        'name': 'Student',
        'total_study_time': 0,
        'total_sessions': 0,
        'average_focus': 5.0
    }
    ml_model = StudentProductivityML()
    
    return jsonify({
        'success': True,
        'message': 'All data reset!'
    })



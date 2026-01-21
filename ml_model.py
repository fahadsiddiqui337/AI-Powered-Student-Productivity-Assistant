"""
Machine Learning Model for Student Productivity
This file contains AI that learns from your study habits!
"""

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import json

class StudentProductivityML:
    """
    This class is like a smart robot that learns:
    - When you study best
    - How long you should study
    - When you need breaks
    """
    
    def __init__(self):
        # Initialize the ML model (like teaching a student for the first time)
        self.focus_predictor = LinearRegression()
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def prepare_features(self, study_sessions):
        """
        Convert study data into numbers the ML model can understand.
        Like translating English to Math!
        
        Features we use:
        - Hour of day (0-23)
        - Day of week (0-6)
        - Study duration (minutes)
        - Number of breaks taken
        """
        if not study_sessions or len(study_sessions) < 3:
            return None, None
            
        features = []
        focus_scores = []
        
        for session in study_sessions:
            # Extract features from each study session
            hour = session.get('hour', 14)
            day = session.get('day_of_week', 1)
            duration = session.get('duration', 30)
            breaks = session.get('breaks', 0)
            focus = session.get('focus_score', 5)
            
            # Create feature vector (list of numbers)
            features.append([hour, day, duration, breaks])
            focus_scores.append(focus)
        
        return np.array(features), np.array(focus_scores)
    
    def train(self, study_sessions):
        """
        Train the ML model with your study history.
        The more you use it, the smarter it gets!
        """
        X, y = self.prepare_features(study_sessions)
        
        if X is None or len(X) < 3:
            return False
        
        try:
            # Normalize the data (make all numbers comparable)
            X_scaled = self.scaler.fit_transform(X)
            
            # Train the model (this is where the magic happens!)
            self.focus_predictor.fit(X_scaled, y)
            self.is_trained = True
            
            return True
        except Exception as e:
            print(f"Training error: {e}")
            return False
    
    def predict_focus_score(self, hour, day_of_week, duration, breaks):
        """
        Predict how focused you'll be during a study session.
        Returns a score from 1-10 (10 = super focused!)
        """
        if not self.is_trained:
            # If not trained yet, return average score
            return 5.0
        
        try:
            # Prepare the input
            features = np.array([[hour, day_of_week, duration, breaks]])
            features_scaled = self.scaler.transform(features)
            
            # Make prediction
            prediction = self.focus_predictor.predict(features_scaled)[0]
            
            # Keep score between 1 and 10
            return max(1.0, min(10.0, prediction))
        except Exception as e:
            print(f"Prediction error: {e}")
            return 5.0
    
    def get_best_study_time(self, study_sessions):
        """
        Analyze when you study best and recommend optimal times.
        """
        if not study_sessions or len(study_sessions) < 3:
            return {
                'best_hour': 14,
                'best_day': 'Monday',
                'confidence': 'low'
            }
        
        # Group sessions by hour
        hour_scores = {}
        for session in study_sessions:
            hour = session.get('hour', 14)
            score = session.get('focus_score', 5)
            
            if hour not in hour_scores:
                hour_scores[hour] = []
            hour_scores[hour].append(score)
        
        # Find hour with highest average score
        best_hour = 14
        best_score = 0
        
        for hour, scores in hour_scores.items():
            avg_score = sum(scores) / len(scores)
            if avg_score > best_score:
                best_score = avg_score
                best_hour = hour
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        return {
            'best_hour': best_hour,
            'best_hour_formatted': f"{best_hour}:00",
            'best_day': days[best_hour % 7],
            'average_score': round(best_score, 1),
            'confidence': 'high' if len(study_sessions) >= 10 else 'medium'
        }
    
    def calculate_optimal_duration(self, study_sessions):
        """
        Calculate how long you should study for maximum productivity.
        """
        if not study_sessions or len(study_sessions) < 3:
            return 25  # Default: 25 minutes (Pomodoro technique)
        
        # Find sessions with highest focus scores
        high_focus_sessions = [s for s in study_sessions if s.get('focus_score', 0) >= 7]
        
        if not high_focus_sessions:
            return 25
        
        # Calculate average duration of high-focus sessions
        durations = [s.get('duration', 25) for s in high_focus_sessions]
        optimal = sum(durations) / len(durations)
        
        return round(optimal)
    
    def get_break_recommendation(self, current_duration):
        """
        Recommend when to take a break based on current study time.
        """
        if current_duration < 20:
            return "Keep going! You're in the zone! "
        elif current_duration < 40:
            return "Consider a 5-minute break soon "
        elif current_duration < 60:
            return "Time for a break! Take 10 minutes "
        else:
            return "You've been studying hard! Take a 15-minute break "
    
    def analyze_performance_trend(self, study_sessions):
        """
        Analyze if student performance is improving over time.
        """
        if not study_sessions or len(study_sessions) < 5:
            return {
                'trend': 'neutral',
                'message': 'Not enough data yet. Keep studying!'
            }
        
        # Take last 10 sessions
        recent = study_sessions[-10:]
        scores = [s.get('focus_score', 5) for s in recent]
        
        # Simple trend analysis
        first_half = scores[:len(scores)//2]
        second_half = scores[len(scores)//2:]
        
        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        
        if avg_second > avg_first + 0.5:
            return {
                'trend': 'improving',
                'message': ' Great job! Your focus is improving!',
                'change': f'+{round(avg_second - avg_first, 1)}'
            }
        elif avg_second < avg_first - 0.5:
            return {
                'trend': 'declining',
                'message': ' Let\'s work on getting back on track!',
                'change': f'{round(avg_second - avg_first, 1)}'
            }
        else:
            return {
                'trend': 'stable',
                'message': '➡️ Consistent performance! Keep it up!',
                'change': '±0'
            }


# Helper function to generate AI study advice
def get_study_advice(performance_data):
    """
    Generate personalized study advice based on ML insights.
    """
    advice = []
    
    # Analyze average focus score
    avg_focus = performance_data.get('average_focus', 5)
    
    if avg_focus >= 8:
        advice.append(" Excellent focus! You're a productivity superstar!")
    elif avg_focus >= 6:
        advice.append(" Good focus! Try studying in 25-minute bursts.")
    else:
        advice.append(" Try the Pomodoro Technique: 25 min study + 5 min break")
    
    # Study duration advice
    total_time = performance_data.get('total_study_time', 0)
    if total_time < 120:  # Less than 2 hours
        advice.append(" Aim for at least 2 hours of focused study daily")
    elif total_time > 300:  # More than 5 hours
        advice.append(" Don't burn out! Quality > Quantity. Take breaks!")
    
    return advice
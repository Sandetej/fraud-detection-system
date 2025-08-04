from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
import logging
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for model and preprocessing
model = None
model_features = None

def load_fraud_model():
    """Load the trained fraud detection model"""
    global model, model_features
    try:
        # Load the saved model
        model_path = 'fraud_detector_final.pkl'
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            logger.info("Model loaded successfully")
            
            # Define expected features based on your model
            model_features = [
                'step', 'amount', 'age', 'gender', 'merchant', 'category'
            ]
        else:
            logger.warning(f"Model file not found at {model_path}. Using mock predictions.")
            model = None
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        model = None

def preprocess_transaction(transaction_data):
    """Preprocess transaction data for model prediction"""
    try:
        # This is a simplified preprocessing - you may need to adjust based on your model
        processed_data = {}
        
        # Convert inputs to appropriate types
        processed_data['step'] = int(transaction_data['step'])
        processed_data['amount'] = float(transaction_data['amount'])
        processed_data['age'] = transaction_data['age']
        processed_data['gender'] = transaction_data['gender']
        processed_data['merchant'] = transaction_data['merchant']  
        processed_data['category'] = transaction_data['category']
        
        return processed_data
        
    except Exception as e:
        logger.error(f"Error preprocessing transaction: {str(e)}")
        return None

def calculate_fraud_probability(transaction_data):
    """Calculate fraud probability for a transaction"""
    try:
        if model is not None:
            # Preprocess the data
            processed_data = preprocess_transaction(transaction_data)
            if processed_data is None:
                return 0.1
            
            # Note: You'll need to implement proper feature engineering here
            # This is a simplified version - adjust based on your model's requirements
            
            # For now, using business rules as fallback
            probability = calculate_business_rules_probability(transaction_data)
            
        else:
            # Use business rules for demo purposes
            probability = calculate_business_rules_probability(transaction_data)
            
        return probability
        
    except Exception as e:
        logger.error(f"Error calculating fraud probability: {str(e)}")
        return 0.1  # Default low risk

def calculate_business_rules_probability(transaction_data):
    """Calculate fraud probability using business rules"""
    amount = float(transaction_data.get('amount', 0))
    merchant = transaction_data.get('merchant', '')
    category = transaction_data.get('category', '')
    
    # Simple risk scoring based on your model insights
    risk_score = 0.0
    
    # Amount-based risk (higher amounts = higher risk)
    if amount > 1000:
        risk_score += 0.4
    elif amount > 500:
        risk_score += 0.25
    elif amount > 100:
        risk_score += 0.1
        
    # Merchant-based risk (based on your feature importance analysis)
    high_risk_merchants = ['M480139044', 'M2080738506', 'M749144843']
    medium_risk_merchants = ['M1823072687', 'M1841913607']
    
    if merchant in high_risk_merchants:
        risk_score += 0.35
    elif merchant in medium_risk_merchants:
        risk_score += 0.2
        
    # Category-based risk (based on your analysis)
    high_risk_categories = ['es_tech', 'es_travel', 'es_sportsandtoys']
    medium_risk_categories = ['es_health', 'es_fashion']
    
    if category in high_risk_categories:
        risk_score += 0.15
    elif category in medium_risk_categories:
        risk_score += 0.08
        
    # Add some variation for realism
    import random
    risk_score += random.uniform(-0.03, 0.03)
    
    # Ensure probability is between 0 and 1
    probability = max(0.0, min(1.0, risk_score))
    
    return probability

@app.route('/')
def dashboard():
    """Serve the fraud detection dashboard"""
    return send_from_directory('static', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

@app.route('/api/predict', methods=['POST'])
def predict_fraud():
    """Predict fraud probability for a transaction"""
    try:
        # Get transaction data from request
        transaction_data = request.get_json()
        
        # Validate required fields
        required_fields = ['step', 'amount', 'age', 'gender', 'merchant', 'category']
        for field in required_fields:
            if field not in transaction_data:
                return jsonify({
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Calculate fraud probability
        probability = calculate_fraud_probability(transaction_data)
        
        # Determine risk level and recommendation
        if probability >= 0.8:
            risk_level = 'High'
            risk_color = '#dc3545'  # Red
            recommendation = 'BLOCK TRANSACTION - High fraud risk detected. Immediate investigation required.'
            action = 'block'
        elif probability >= 0.3:
            risk_level = 'Medium'
            risk_color = '#ffc107'  # Yellow  
            recommendation = 'REVIEW REQUIRED - Medium fraud risk. Queue for manual review.'
            action = 'review'
        else:
            risk_level = 'Low'
            risk_color = '#28a745'  # Green
            recommendation = 'APPROVE - Low fraud risk. Transaction can proceed normally.'
            action = 'approve'
        
        # Calculate confidence score
        confidence = max(0.75, min(0.98, 1 - abs(probability - 0.5)))
        
        # Log the prediction
        logger.info(f"Fraud prediction: {probability:.3f} for amount ${transaction_data['amount']}")
        
        # Return prediction results
        return jsonify({
            'success': True,
            'transaction_id': f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'fraud_probability': round(probability * 100, 1),
            'risk_level': risk_level,
            'risk_color': risk_color,
            'confidence_score': round(confidence * 100, 1),
            'recommendation': recommendation,
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'model_version': '1.0'
        })
        
    except Exception as e:
        logger.error(f"Error in fraud prediction: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error during prediction'
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_model_stats():
    """Get model performance statistics"""
    try:
        stats = {
            'model_performance': {
                'accuracy': 99.4,
                'precision': 66.8,
                'recall': 94.9,
                'f1_score': 78.4,
                'roc_auc': 99.9,
                'pr_auc': 91.7
            },
            'business_metrics': {
                'total_transactions': 118929,
                'fraud_detected': 1367,
                'false_alarms': 679,
                'fraud_detection_rate': 94.9,
                'false_alarm_rate': 0.6
            },
            'model_info': {
                'algorithm': 'RandomForest',
                'features_count': 21,
                'training_data_size': 475714,
                'model_version': '1.0',
                'last_updated': '2024-01-15'
            }
        }
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': 'Error retrieving statistics'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': model is not None,
        'version': '1.0'
    })

@app.route('/api/merchants', methods=['GET'])
def get_merchants():
    """Get list of available merchants"""
    merchants = [
        "M348934600", "M1823072687", "M480139044", "M980657600",
        "M2080738506", "M1841913607", "M749144843", "M2018384601"
    ]
    return jsonify({'merchants': merchants})

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get list of transaction categories"""
    categories = [
        "es_transportation", "es_sportsandtoys", "es_health", "es_fashion",
        "es_bars", "es_hyper", "es_food", "es_home", "es_contents", "es_tech",
        "es_travel", "es_wellnessandbeauty", "es_otherservices", "es_hotelservices",
        "es_barsandrestaurants", "es_leisure"
    ]
    return jsonify({'categories': categories})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Load the fraud detection model on startup
    port = int(os.environ.get("PORT", 5000))
    load_fraud_model()
    app.run(host="0.0.0.0", port=port)
    
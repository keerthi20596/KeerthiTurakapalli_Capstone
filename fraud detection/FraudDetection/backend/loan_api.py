from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import pandas as pd
import numpy as np
import pickle
from rejection_handler import (
    save_rejected_application, send_rejection_email,
    get_rejected_applications, get_rejection_stats, init_database
)

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, 'loan_model.pkl')
SCALER_PATH = os.path.join(BASE_DIR, 'scaler.pkl')

app = Flask(__name__, static_folder=BASE_DIR, template_folder=BASE_DIR)
CORS(app)

# Initialize database on startup
init_database()


def load_model_and_scaler():
    if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
        return None, None
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    with open(SCALER_PATH, 'rb') as f:
        scaler = pickle.load(f)
    return model, scaler


def preprocess_input(df):
    # Basic cleaning and mapping consistent with training
    df = df.copy()
    df.columns = df.columns.str.strip()
    if 'education' in df.columns and df['education'].dtype == object:
        df['education'] = df['education'].str.strip().map({'Graduate':1, 'Not Graduate':0})
    if 'self_employed' in df.columns and df['self_employed'].dtype == object:
        df['self_employed'] = df['self_employed'].str.strip().map({'Yes':1, 'No':0})
    # select numeric features
    X = df.select_dtypes(include=[np.number]).fillna(0)
    # Drop target and id columns if present
    X = X.drop(columns=['loan_status', 'loan_id'], errors='ignore')
    return X


@app.route('/', methods=['GET'])
def home():
    return send_from_directory(BASE_DIR, 'index.html')


@app.route('/health', methods=['GET'])
def health():
    model, scaler = load_model_and_scaler()
    return jsonify({'status':'ok', 'model_loaded': model is not None})


@app.route('/predict', methods=['POST'])
def predict():
    model, scaler = load_model_and_scaler()
    if model is None or scaler is None:
        return jsonify({'error':'Model not trained. Run training first.'}), 400

    # Accept JSON single record or CSV file upload
    applicant_email = None
    applicant_name = None
    if request.files and 'file' in request.files:
        file = request.files['file']
        df = pd.read_csv(file)
        df_original = df.copy()  # Keep original data with all fields
        X = preprocess_input(df)
    else:
        payload = request.get_json(force=True)
        # Extract email and name from payload if provided
        if isinstance(payload, dict):
            applicant_email = payload.get('email') or payload.get('applicant_email')
            applicant_name = payload.get('applicant_name')
            df = pd.DataFrame([payload])
        elif isinstance(payload, list):
            df = pd.DataFrame(payload)
        else:
            return jsonify({'error':'Invalid JSON payload'}), 400
        df_original = df.copy()  # Keep original data with all fields
        X = preprocess_input(df)

    # align columns to scaler / training features
    try:
        X_scaled = scaler.transform(X)
    except ValueError as e:
        # If feature names don't match, try to reindex to scaler feature names
        feature_names = scaler.get_feature_names_out() if hasattr(scaler, 'get_feature_names_out') else None
        if feature_names is not None:
            X = X.reindex(columns=feature_names, fill_value=0)
        X_scaled = scaler.transform(X)

    probs = model.predict_proba(X_scaled)[:,1] if hasattr(model, 'predict_proba') else None
    preds = model.predict(X_scaled)

    results = []
    for i in range(len(preds)):
        approved = bool(preds[i])
        probability = float(probs[i]) if probs is not None else None
        
        result = {
            'index': int(i),
            'approved': approved,
            'probability': probability
        }
        
        # If rejected, save to database and send email notification
        if not approved:
            # Get the original data for this row (before preprocessing)
            original_data = df_original.iloc[i].to_dict()
            
            # Use the email and name extracted earlier from the payload
            email_to_use = applicant_email or original_data.get('email') or original_data.get('applicant_email')
            name_to_use = applicant_name or original_data.get('applicant_name', 'Applicant')
            
            # Save to database
            save_rejected_application(original_data, 1 - probability, email_to_use)
            
            # Send email if email provided
            if email_to_use:
                email_sent = send_rejection_email(
                    name_to_use,
                    email_to_use,
                    original_data,
                    1 - probability
                )
                result['email_sent'] = email_sent
                if not email_sent:
                    result['email_warning'] = 'Email notification failed - check server configuration'
            else:
                result['email_sent'] = False
                result['email_warning'] = 'No email address provided'
        
        results.append(result)

    return jsonify(results)


@app.route('/admin/rejected-applications', methods=['GET'])
def admin_rejected_applications():
    """Get all rejected applications (admin endpoint)"""
    applications = get_rejected_applications()
    return jsonify(applications)


@app.route('/admin/rejection-stats', methods=['GET'])
def admin_rejection_stats():
    """Get statistics on rejected applications"""
    stats = get_rejection_stats()
    return jsonify(stats)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

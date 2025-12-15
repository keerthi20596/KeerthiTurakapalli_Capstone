from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import pickle
import os

# Try to import pipeline module (optional). If unavailable, app will continue to work.
try:
    import Pipeline as pipeline_module
    process_transaction = getattr(pipeline_module, 'process_transaction', None)
    send_sms_only = getattr(pipeline_module, 'send_sms_only', None)
    PIPELINE_AVAILABLE = process_transaction is not None
except (ImportError, ModuleNotFoundError):
    process_transaction = None
    send_sms_only = None
    PIPELINE_AVAILABLE = False

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Load the Model
model = pickle.load(open('model_rndf.pkl', 'rb'))

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles file upload and fraud detection."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"})
    
    df = pd.read_csv(file)
    
    # Model expects only 2 features: 'amount' and 'time'
    # Map common column names to these expected features
    amount_col = None
    time_col = None
    
    # Find amount column (try common names)
    for col in df.columns:
        col_lower = col.lower()
        if 'amount' in col_lower and amount_col is None:
            amount_col = col
            break
    
    # Find time column — prefer Hour, Day, or similar numeric time columns over Timestamp
    for col in df.columns:
        col_lower = col.lower()
        if col_lower in ['hour', 'day', 'minute', 'time']:
            time_col = col
            break
    # If no numeric time column found, try to extract hour from Timestamp
    if time_col is None and 'Timestamp' in df.columns:
        df['Hour'] = pd.to_datetime(df['Timestamp'], errors='coerce').dt.hour
        time_col = 'Hour'
    
    if amount_col is None or time_col is None:
        return jsonify({
            'error': f'CSV must contain amount and time columns. Found: {df.columns.tolist()}'
        }), 400
    
    # Prepare data with only the 2 required features, ensure they are numeric
    df_subset = df[[amount_col, time_col]].copy()
    df_subset[amount_col] = pd.to_numeric(df_subset[amount_col], errors='coerce')
    df_subset[time_col] = pd.to_numeric(df_subset[time_col], errors='coerce')
    
    # Drop rows with NaN values
    df_subset = df_subset.dropna()
    
    if df_subset.empty:
        return jsonify({'error': 'No valid numeric data found in amount and time columns'}), 400
    
    data = df_subset.values.tolist()

    # Predict
    predictions = model.predict(data)

    # Try to get fraud probabilities if model supports it
    fraud_probas = None
    try:
        if hasattr(model, 'predict_proba'):
            fraud_probas = model.predict_proba(data)[:, 1]
    except Exception:
        fraud_probas = None

    result = []
    # Iterate rows and, if pipeline is available, process each transaction
    for i, pred in enumerate(predictions):
        fraud_flag = int(bool(pred))
        prob = float(fraud_probas[i]) if fraud_probas is not None else None

        pipeline_info = None
        if PIPELINE_AVAILABLE and process_transaction is not None:
            try:
                tx = df.iloc[i].to_dict()
                pipeline_info = process_transaction(tx, fraud_flag, fraud_probability=prob)
            except Exception as e:
                pipeline_info = {'error': f'pipeline failure: {e}'}

        result.append({
            'transaction': i+1,
            'fraud': bool(pred),
            'fraud_probability': prob,
            'pipeline': pipeline_info
        })

    return jsonify(result)

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "API is working!"})


@app.route('/pipeline_test', methods=['POST', 'GET'])
def pipeline_test():
    """Quick route to test the pipeline actions.

    Sends a sample transaction through process_transaction and returns the result.
    Use POST with JSON to provide a custom transaction payload.
    """
    if not PIPELINE_AVAILABLE or process_transaction is None:
        return jsonify({'error': 'pipeline not available on server'}), 503

    sample_tx = {
        'customer': 'TEST_USER',
        'amount': 1234.56,
        'type': 'TRANSFER',
        'orig': 'ACC000',
        'dest': 'ACC999'
    }

    # Allow overriding via POST JSON
    if request.method == 'POST' and request.is_json:
        try:
            sample_tx = request.get_json()
        except Exception:
            pass

    # Simulate fraud_flag=1 to trigger notification/blocking
    try:
        res = process_transaction(sample_tx, fraud_flag=1, fraud_probability=0.95)
        return jsonify({'pipeline_test': res})
    except Exception as e:
        return jsonify({'error': f'pipeline invocation failed: {e}'}), 500


@app.route('/pipeline_test_no_fraud', methods=['POST', 'GET'])
def pipeline_test_no_fraud():
    """Test route that simulates a non-fraud transaction (fraud_flag=0).

    Returns the pipeline response so you can verify the pipeline leaves legitimate transactions alone.
    """
    if not PIPELINE_AVAILABLE or process_transaction is None:
        return jsonify({'error': 'pipeline not available on server'}), 503

    sample_tx = {
        'customer': 'TEST_USER',
        'amount': 50.00,
        'type': 'PAYMENT',
        'orig': 'ACC100',
        'dest': 'ACC200'
    }

    if request.method == 'POST' and request.is_json:
        try:
            sample_tx = request.get_json()
        except Exception:
            pass

    try:
        res = process_transaction(sample_tx, fraud_flag=0, fraud_probability=0.01)
        return jsonify({'pipeline_test_no_fraud': res})
    except Exception as e:
        return jsonify({'error': f'pipeline invocation failed: {e}'}), 500


@app.route('/pipeline_sms_test', methods=['POST', 'GET'])
def pipeline_sms_test():
    """Endpoint to test sending an SMS via Twilio only.

    GET: sends a test SMS to the `NOTIFY_PHONE` env var with a default body.
    POST (JSON): accepts `{ "to": "+123...", "body": "message text" }`.
    """
    if send_sms_only is None:
        return jsonify({'error': 'SMS test not available: send_sms_only not implemented'}), 503

    to_number = os.environ.get('NOTIFY_PHONE')
    body = 'Test SMS from FraudDetection pipeline'

    if request.method == 'POST' and request.is_json:
        try:
            payload = request.get_json()
            to_number = payload.get('to', to_number)
            body = payload.get('body', body)
        except Exception:
            pass

    if not to_number:
        return jsonify({'error': 'No destination phone configured. Set NOTIFY_PHONE env var or POST JSON with "to".'}), 400

    try:
        res = send_sms_only(to_number, body)
        return jsonify({'sms_test': res})
    except Exception as e:
        return jsonify({'error': f'sms invocation failed: {e}'}), 500

if __name__ == '__main__':
    app.run(debug=True)

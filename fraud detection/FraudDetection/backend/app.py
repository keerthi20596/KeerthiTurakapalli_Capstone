from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import pickle

app = Flask(__name__)

# Load the trained XGBClassifier model
model = joblib.load("xgb_model.pkl")

# Features used during training
features = [
    'amount_paid', 'sender_bank', 'receiver_bank', 'receiving_currency',
    'payment_currency', 'payment_format', 'transaction_difference',
    'transaction_difference_percentage', 'log_amount_received', 'log_amount_paid',
    'rolling_mean_amount_7d', 'rolling_std_amount_7d', 'hour', 'day_of_week',
    'is_weekend', 'num_transactions_30d', 'avg_transaction_30d',
    'degree_centrality', 'pagerank_score', 'cross_currency_transaction',
    'time_diff', 'is_burst', 'z_score_amount', 'is_anomalous_amount',
    'is_circular', 'currency_arbitrage'
] + [f"gnn_embedding_{i}" for i in range(1, 17)]

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"})
    
    df = pd.read_csv(file)
    
    # Prepare data for model
    data = df.values.tolist()
    
    # Predict
    predictions = model.predict(data)
    
    result = [{'transaction': i+1, 'fraud': bool(pred)} for i, pred in enumerate(predictions)]
    
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

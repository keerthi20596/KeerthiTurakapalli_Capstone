from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import pickle
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Load the trained model
model = pickle.load(open("model_rndf.pkl", "rb"))

# Must match training feature names EXACTLY
features = [
    "Amount Paid",
    "ParsedTime",
    "FromBank",
    "ToBank",
    "Received Currency",
    "Payment Currency",
    "Payment Format"
]

def parse_timestamp(ts):
    try:
        parts = str(ts).split()[1].split(":")
        return int(parts[0]) * 3600 + int(parts[1]) * 60
    except:
        return 0

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    filename = file.filename.strip()
    if not filename:
        return jsonify({"error": "No file selected"}), 400

    ext = os.path.splitext(filename)[-1].lower()

    try:
        # Load file
        if ext == '.csv':
            df = pd.read_csv(file)
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file, engine='openpyxl')
        else:
            return jsonify({"error": "Unsupported file format"}), 400

        # Clean column names
        df.columns = df.columns.str.strip()
        df.columns = [col.lower() for col in df.columns]

        # Rename to match training
        rename_map = {
            'timestamp': 'TimeStamp',
            'frombank': 'FromBank',
            'tobank': 'ToBank',
            'account': 'Account',
            'amount paid': 'Amount Paid',
            'received currency': 'Received Currency',
            'payment currency': 'Payment Currency',
            'payment format': 'Payment Format'
        }
        df.rename(columns=rename_map, inplace=True)

        # Validate required columns
        required = ["TimeStamp", "FromBank", "ToBank", "Account", "Amount Paid", 
                    "Received Currency", "Payment Currency", "Payment Format"]
        for col in required:
            if col not in df.columns:
                return jsonify({"error": f"Missing required column: {col}"}), 400

        # Parse timestamp
        df["ParsedTime"] = df["TimeStamp"].apply(parse_timestamp)

        # Save original display values
        df["Currency_Display"] = df["Received Currency"]
        df["Format_Display"] = df["Payment Format"]

        # Encode for model
        for col in ["Received Currency", "Payment Currency", "Payment Format"]:
            df[col] = df[col].astype('category').cat.codes

        # Match training features
        X = df[features]
        preds = model.predict(X)

        # Prepare results
        results = []
        for i, row in df.iterrows():
            results.append({
                "transaction": i + 1,
                "from_bank": row["FromBank"],
                "from_account": row["Account"],
                "to_bank": row["ToBank"],
                "amount": float(row["Amount Paid"]),
                "status": "Fraud" if preds[i] else "Legit",
                "received_currency": row["Currency_Display"],
                "payment_format": row["Format_Display"]
            })

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": f"Backend error: {str(e)}"}), 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "API is working!"})

if __name__ == '__main__':
    app.run(debug=True)

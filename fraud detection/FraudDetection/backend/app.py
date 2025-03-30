from flask import Flask, request, jsonify
import pandas as pd
import pickle

app = Flask(__name__)

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
    
    # Prepare data for model
    data = df.values.tolist()
    
    # Predict
    predictions = model.predict(data)
    
    result = [{'transaction': i+1, 'fraud': bool(pred)} for i, pred in enumerate(predictions)]
    
    return jsonify(result)

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "API is working!"})

if __name__ == '__main__':
    app.run(debug=True)

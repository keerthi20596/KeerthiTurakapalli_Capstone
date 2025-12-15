Loan Approval AI - Backend

Files added/updated:
- `train_loan_model.py` — unified training script, saves `loan_model.pkl` and `scaler.pkl` in this folder.
- `loan_api.py` — Flask API exposing `/health` and `/predict`.
- `requirements.txt` — updated with required packages.

Quick start (from this backend folder):

1. (Optional) create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install requirements:

```powershell
pip install -r requirements.txt
```

3. Train the model (saves `loan_model.pkl` and `scaler.pkl`):

```powershell
python train_loan_model.py
```

4. Start the API:

```powershell
python loan_api.py
```

5. Example predict (JSON single record):

POST `http://localhost:5001/predict` with JSON body matching your dataset columns. The API will auto-preprocess numeric features.

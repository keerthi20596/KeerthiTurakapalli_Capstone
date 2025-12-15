# Quick Start Checklist

Use this checklist to quickly set up and run the AI Loan Approval System.

## Pre-Flight Checks
- [ ] Python 3.8+ installed (`python --version`)
- [ ] In correct directory: `fraud detection\FraudDetection\backend`
- [ ] Dataset file exists: `C:\Users\keerthi\Downloads\loan_approval_dataset.csv`
- [ ] All requirements satisfied

## Installation (5 minutes)
- [ ] Run: `pip install -r requirements.txt`
- [ ] Wait for installation to complete

## Model Training (1-2 minutes)
- [ ] Run: `python train_loan_model.py`
- [ ] Verify output shows ~98% accuracy
- [ ] Check for `loan_model.pkl` and `scaler.pkl` files

## Optional: Email Configuration (2 minutes)
- [ ] Open: `rejection_handler.py`
- [ ] Set `SENDER_EMAIL` to your Gmail address
- [ ] Get Gmail App Password from: https://myaccount.google.com/apppasswords
- [ ] Set `SENDER_PASSWORD` to the 16-character app password
- [ ] Save file

## Start Backend API (1 minute)
- [ ] Run: `python loan_api.py`
- [ ] Wait for message: "Running on http://0.0.0.0:5001"
- [ ] Keep terminal open

## Test the System (5 minutes)
- [ ] Open browser: `http://localhost:5001`
- [ ] See the loan application form
- [ ] Fill test case 1 (Approval scenario)
- [ ] Submit form
- [ ] Verify "✓ APPROVED" result
- [ ] Fill test case 2 (Rejection scenario)
- [ ] Submit form
- [ ] Verify "✗ REJECTED" result
- [ ] (Optional) Check email for rejection notification

## Success! 🎉
Your AI Loan Approval System is running!

---

## Common Issues Quick Fixes

**Model not found?**
→ Run `python train_loan_model.py`

**Port 5001 in use?**
→ Kill process: `netstat -ano | findstr :5001` then `taskkill /PID <PID> /F`

**Dataset not found?**
→ Place CSV at `C:\Users\keerthi\Downloads\loan_approval_dataset.csv`

**Email not working?**
→ Verify Gmail App Password (not regular password) is correctly set

**CORS error?**
→ Already handled in code, refresh browser

---

## API Documentation

All endpoints available after Step 6:

```
Health Check:
GET http://localhost:5001/health

Make Prediction:
POST http://localhost:5001/predict
(JSON body with applicant data)

Admin - View Rejections:
GET http://localhost:5001/admin/rejected-applications

Admin - Rejection Stats:
GET http://localhost:5001/admin/rejection-stats
```

---

For detailed setup guide, see: `SETUP_AND_RUN_GUIDE.md`

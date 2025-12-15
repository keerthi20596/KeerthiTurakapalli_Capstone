# 🧪 Testing Guide - AI Loan Approval System

Complete testing procedures for the AI Loan Approval System.

---

## 📋 Test Setup

Before running tests:

1. **Install dependencies:**
```powershell
pip install -r requirements.txt
```

2. **Train the model:**
```powershell
python train_loan_model.py
```

3. **Start the API:**
```powershell
python loan_api.py
```

Keep the API running in a terminal window while testing.

---

## 🧪 Test Suite 1: API Endpoints

### Test 1.1: Health Check
**Endpoint:** `GET /health`

**Command:**
```powershell
$response = Invoke-WebRequest -Uri "http://localhost:5001/health" -Method Get
$response.Content
```

**Expected Response:**
```json
{"status": "ok", "model_loaded": true}
```

**Status:** ✅ Pass / ❌ Fail

---

### Test 1.2: Web UI Load
**Endpoint:** `GET /`

**Steps:**
1. Open browser
2. Navigate to `http://localhost:5001`
3. Verify form loads with all fields

**Expected Result:**
- Form displays with gradient background
- All input fields visible
- Submit button displays

**Status:** ✅ Pass / ❌ Fail

---

### Test 1.3: Single Prediction - Approval
**Endpoint:** `POST /predict`

**Command:**
```powershell
$body = @{
    income_annum = 5000000
    loan_amount = 1500000
    loan_term = 12
    cibil_score = 800
    education = "Graduate"
    self_employed = "No"
    no_of_dependents = 0
    residential_assets_value = 2000000
    commercial_assets_value = 1000000
    luxury_assets_value = 500000
    bank_asset_value = 300000
    email = "test_approval@example.com"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5001/predict" -Method Post `
    -ContentType "application/json" `
    -Body $body | Select-Object -ExpandProperty Content
```

**Expected Response:**
```json
[{
    "approved": true,
    "probability": 0.95,
    "index": 0
}]
```

**Validation Criteria:**
- ✅ `approved` is `true`
- ✅ `probability` > 0.8
- ✅ Response time < 200ms

**Status:** ✅ Pass / ❌ Fail

---

### Test 1.4: Single Prediction - Rejection
**Endpoint:** `POST /predict`

**Command:**
```powershell
$body = @{
    income_annum = 300000
    loan_amount = 5000000
    loan_term = 60
    cibil_score = 400
    education = "Not Graduate"
    self_employed = "Yes"
    no_of_dependents = 5
    residential_assets_value = 100000
    commercial_assets_value = 50000
    luxury_assets_value = 0
    bank_asset_value = 10000
    email = "test_rejection@example.com"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5001/predict" -Method Post `
    -ContentType "application/json" `
    -Body $body | Select-Object -ExpandProperty Content
```

**Expected Response:**
```json
[{
    "approved": false,
    "probability": 0.15,
    "index": 0
}]
```

**Validation Criteria:**
- ✅ `approved` is `false`
- ✅ `probability` < 0.5 (rejection probability)
- ✅ Response time < 200ms

**Status:** ✅ Pass / ❌ Fail

---

### Test 1.5: Batch Predictions
**Endpoint:** `POST /predict`

**Command:**
```powershell
$body = @(
    @{
        income_annum = 5000000
        loan_amount = 1500000
        loan_term = 12
        cibil_score = 800
        education = "Graduate"
        self_employed = "No"
        no_of_dependents = 0
        residential_assets_value = 2000000
        commercial_assets_value = 1000000
        luxury_assets_value = 500000
        bank_asset_value = 300000
        email = "batch1@example.com"
    },
    @{
        income_annum = 300000
        loan_amount = 5000000
        loan_term = 60
        cibil_score = 400
        education = "Not Graduate"
        self_employed = "Yes"
        no_of_dependents = 5
        residential_assets_value = 100000
        commercial_assets_value = 50000
        luxury_assets_value = 0
        bank_asset_value = 10000
        email = "batch2@example.com"
    }
) | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5001/predict" -Method Post `
    -ContentType "application/json" `
    -Body $body | Select-Object -ExpandProperty Content
```

**Expected Response:**
```json
[
    {"approved": true, "probability": 0.95, "index": 0},
    {"approved": false, "probability": 0.15, "index": 1}
]
```

**Validation Criteria:**
- ✅ Returns array with 2 elements
- ✅ First result approved, second rejected
- ✅ Response time < 300ms for 2 predictions

**Status:** ✅ Pass / ❌ Fail

---

### Test 1.6: Admin - View Rejected Applications
**Endpoint:** `GET /admin/rejected-applications`

**Prerequisites:**
- Run Test 1.4 first to create a rejection record

**Command:**
```powershell
Invoke-WebRequest -Uri "http://localhost:5001/admin/rejected-applications" -Method Get | Select-Object -ExpandProperty Content
```

**Expected Response:**
```json
[
    {
        "id": 1,
        "application_date": "2025-01-15 10:30:00",
        "income_annum": 300000,
        "loan_amount": 5000000,
        "cibil_score": 400,
        "rejection_probability": 0.85,
        "rejection_reason": "Low credit score & High debt-to-income ratio",
        "email_sent": false,
        "email_address": "test_rejection@example.com"
    }
]
```

**Validation Criteria:**
- ✅ Returns array
- ✅ Contains rejected applications
- ✅ All required fields present

**Status:** ✅ Pass / ❌ Fail

---

### Test 1.7: Admin - Rejection Statistics
**Endpoint:** `GET /admin/rejection-stats`

**Command:**
```powershell
Invoke-WebRequest -Uri "http://localhost:5001/admin/rejection-stats" -Method Get | Select-Object -ExpandProperty Content
```

**Expected Response:**
```json
{
    "total_rejected": 1,
    "emails_sent": 0,
    "avg_credit_score": 400,
    "avg_debt_to_income": 16.67
}
```

**Validation Criteria:**
- ✅ Returns JSON object
- ✅ `total_rejected` >= 1
- ✅ All statistics calculated correctly

**Status:** ✅ Pass / ❌ Fail

---

## 🎨 Test Suite 2: Web UI

### Test 2.1: Form Field Validation
**Steps:**
1. Open `http://localhost:5001`
2. Try submitting form with empty fields
3. Verify HTML5 validation error messages

**Expected Result:**
- ✅ Required field error messages appear
- ✅ Form prevents submission

**Status:** ✅ Pass / ❌ Fail

---

### Test 2.2: Form Submission - Approval
**Steps:**
1. Open `http://localhost:5001`
2. Fill with approval scenario data:
   - Income: 5000000
   - Loan: 1500000
   - Term: 12
   - Score: 800
   - Education: Graduate
   - Employment: Employed
   - Dependents: 0
   - Assets: 2M + 1M + 500K + 300K
   - Email: test@example.com
3. Click "Check Loan Eligibility"

**Expected Result:**
- ✅ Loading spinner appears
- ✅ "✓ APPROVED" badge displays
- ✅ Confidence bar shows ~95%
- ✅ Details section shows financial analysis

**Status:** ✅ Pass / ❌ Fail

---

### Test 2.3: Form Submission - Rejection
**Steps:**
1. Open `http://localhost:5001`
2. Fill with rejection scenario data:
   - Income: 300000
   - Loan: 5000000
   - Term: 60
   - Score: 400
   - Education: Not Graduate
   - Employment: Self-Employed
   - Dependents: 5
   - Assets: 100K + 50K + 0 + 10K
   - Email: rejection@example.com
3. Click "Check Loan Eligibility"

**Expected Result:**
- ✅ Loading spinner appears
- ✅ "✗ REJECTED" badge displays (red)
- ✅ Confidence bar shows rejection reason
- ✅ "Check Another Application" button visible

**Status:** ✅ Pass / ❌ Fail

---

### Test 2.4: Reset Form
**Steps:**
1. Submit a prediction
2. Results display
3. Click "Check Another Application"

**Expected Result:**
- ✅ Form clears
- ✅ Results hide
- ✅ Form is ready for new input

**Status:** ✅ Pass / ❌ Fail

---

### Test 2.5: Responsive Design
**Steps:**
1. Open `http://localhost:5001`
2. Resize browser to mobile width (375px)
3. Verify layout adjusts

**Expected Result:**
- ✅ Form stacks vertically
- ✅ All fields readable
- ✅ Button spans full width
- ✅ No horizontal scrolling

**Status:** ✅ Pass / ❌ Fail

---

## 💾 Test Suite 3: Database

### Test 3.1: Database Creation
**Steps:**
1. Check if `rejected_applications.db` exists in backend folder
2. If not, run a rejection prediction to create it

**Expected Result:**
- ✅ File `rejected_applications.db` exists
- ✅ File size > 0 KB

**Status:** ✅ Pass / ❌ Fail

---

### Test 3.2: Data Persistence
**Steps:**
1. Submit rejection prediction
2. Stop API (Ctrl+C)
3. Restart API
4. Query `/admin/rejected-applications`

**Expected Result:**
- ✅ Previous rejection still in database
- ✅ Data persists across restarts

**Status:** ✅ Pass / ❌ Fail

---

## ✉️ Test Suite 4: Email Notifications

### Test 4.1: Email Configuration Check
**Steps:**
1. Open `rejection_handler.py`
2. Verify SENDER_EMAIL and SENDER_PASSWORD are set
3. Check values are not defaults

**Expected Result:**
- ✅ SENDER_EMAIL is valid Gmail address
- ✅ SENDER_PASSWORD is 16-character app password (not regular password)

**Status:** ✅ Pass / ❌ Fail

### Test 4.2: Email on Rejection
**Prerequisites:**
- Email configured in `rejection_handler.py`

**Steps:**
1. Submit rejection prediction with real email
2. Check email inbox (may take 1-2 minutes)

**Expected Result:**
- ✅ Email received from sender address
- ✅ Subject contains "Loan Application Rejected"
- ✅ Email contains HTML formatted content
- ✅ Includes applicant name, reason, suggestions

**Status:** ✅ Pass / ❌ Fail

---

## ⚡ Test Suite 5: Performance

### Test 5.1: Single Prediction Speed
**Steps:**
1. Submit single prediction
2. Measure response time

**Expected Result:**
- ✅ Response time < 200ms

**Actual:** _____ ms

---

### Test 5.2: Batch Processing Speed
**Steps:**
1. Submit 50 predictions in batch
2. Measure total response time

**Expected Result:**
- ✅ Response time < 5 seconds for 50 predictions

**Actual:** _____ seconds

---

### Test 5.3: Memory Usage
**Steps:**
1. Monitor system memory while API running
2. Submit multiple predictions

**Expected Result:**
- ✅ Memory usage remains stable
- ✅ No memory leaks

**Actual:** _____ MB

---

## 🔒 Test Suite 6: Error Handling

### Test 6.1: Invalid JSON
**Command:**
```powershell
Invoke-WebRequest -Uri "http://localhost:5001/predict" -Method Post `
    -ContentType "application/json" `
    -Body "invalid json" 
```

**Expected Result:**
- ✅ Returns 400 error
- ✅ Error message is descriptive

**Status:** ✅ Pass / ❌ Fail

---

### Test 6.2: Missing Required Field
**Command:**
```powershell
$body = @{
    income_annum = 5000000
    loan_amount = 1500000
    # Missing other fields
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5001/predict" -Method Post `
    -ContentType "application/json" `
    -Body $body
```

**Expected Result:**
- ✅ Returns 400 or 422 error
- ✅ Error indicates missing field

**Status:** ✅ Pass / ❌ Fail

---

### Test 6.3: Invalid Data Type
**Command:**
```powershell
$body = @{
    income_annum = "not a number"
    loan_amount = 1500000
    loan_term = 12
    cibil_score = 750
    education = "Graduate"
    self_employed = "No"
    no_of_dependents = 0
    residential_assets_value = 2000000
    commercial_assets_value = 1000000
    luxury_assets_value = 500000
    bank_asset_value = 300000
    email = "test@example.com"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5001/predict" -Method Post `
    -ContentType "application/json" `
    -Body $body
```

**Expected Result:**
- ✅ Returns error or handles gracefully
- ✅ API doesn't crash

**Status:** ✅ Pass / ❌ Fail

---

## 📊 Test Results Summary

| Test | Status | Notes |
|------|--------|-------|
| 1.1 - Health Check | ⬜ | |
| 1.2 - Web UI Load | ⬜ | |
| 1.3 - Single Prediction (Approval) | ⬜ | |
| 1.4 - Single Prediction (Rejection) | ⬜ | |
| 1.5 - Batch Predictions | ⬜ | |
| 1.6 - Admin Rejected Apps | ⬜ | |
| 1.7 - Admin Stats | ⬜ | |
| 2.1 - Form Validation | ⬜ | |
| 2.2 - Form Submission (Approval) | ⬜ | |
| 2.3 - Form Submission (Rejection) | ⬜ | |
| 2.4 - Reset Form | ⬜ | |
| 2.5 - Responsive Design | ⬜ | |
| 3.1 - Database Creation | ⬜ | |
| 3.2 - Data Persistence | ⬜ | |
| 4.1 - Email Config | ⬜ | |
| 4.2 - Email on Rejection | ⬜ | |
| 5.1 - Single Speed | ⬜ | |
| 5.2 - Batch Speed | ⬜ | |
| 5.3 - Memory | ⬜ | |
| 6.1 - Invalid JSON | ⬜ | |
| 6.2 - Missing Field | ⬜ | |
| 6.3 - Invalid Type | ⬜ | |

**Legend:** ✅ = Pass | ❌ = Fail | ⬜ = Not Tested

---

## 🎯 Success Criteria

**Minimum Requirements:**
- ✅ Tests 1.1, 1.2, 1.3, 1.4 pass (core API functionality)
- ✅ Tests 2.2, 2.3 pass (UI works)
- ✅ Test 3.1 passes (database working)

**Complete System:**
- ✅ All tests pass
- ✅ All error handling works
- ✅ Performance meets targets
- ✅ Email notifications work (if configured)

---

## 📝 Notes

- Record actual response times for performance tests
- Test with realistic data from your dataset
- Test both edge cases (very high/low values) and normal cases
- Verify database file grows as rejections accumulate

---

**Test Plan Created:** January 2025  
**For:** AI Loan Approval System  
**Status:** Ready for Testing

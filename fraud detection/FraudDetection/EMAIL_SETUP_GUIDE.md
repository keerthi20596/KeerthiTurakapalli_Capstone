# Email Notification Setup Guide

## Problem
Email notifications for rejected loan applications are not being sent because the email credentials are not configured.

## Solution

### Option 1: Using Gmail (Recommended)

1. **Enable 2-Step Verification**
   - Go to your Google Account: https://myaccount.google.com/
   - Navigate to Security → 2-Step Verification
   - Enable it if not already enabled

2. **Generate App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select app: "Mail"
   - Select device: "Windows Computer" or "Other"
   - Click "Generate"
   - **Copy the 16-character password** (it will only be shown once)

3. **Configure the Application**
   
   **Method A: Edit the file directly**
   - Open `backend/rejection_handler.py`
   - Find these lines (around line 10-11):
   ```python
   SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your_email@gmail.com")
   SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your_app_password")
   ```
   - Replace with your credentials:
   ```python
   SENDER_EMAIL = os.getenv("SENDER_EMAIL", "youremail@gmail.com")
   SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your-16-char-app-password")
   ```

   **Method B: Use environment variables (more secure)**
   - Create a `.env` file in the `backend` folder:
   ```
   SENDER_EMAIL=youremail@gmail.com
   SENDER_PASSWORD=your-16-char-app-password
   ```
   - In PowerShell terminal, set the variables:
   ```powershell
   $env:SENDER_EMAIL="youremail@gmail.com"
   $env:SENDER_PASSWORD="your-16-char-app-password"
   ```

4. **Restart the Backend Server**
   ```powershell
   cd "fraud detection\FraudDetection\backend"
   python loan_api.py
   ```

### Option 2: Using Other Email Providers

#### Outlook/Hotmail
```python
SENDER_EMAIL = "your_email@outlook.com"
SENDER_PASSWORD = "your_password"
SMTP_SERVER = "smtp-mail.outlook.com"
SMTP_PORT = 587
```

#### Yahoo Mail
```python
SENDER_EMAIL = "your_email@yahoo.com"
SENDER_PASSWORD = "your_app_password"  # Generate at Yahoo Account Security
SMTP_SERVER = "smtp.mail.yahoo.com"
SMTP_PORT = 587
```

#### Custom SMTP Server
```python
SENDER_EMAIL = "your_email@yourdomain.com"
SENDER_PASSWORD = "your_password"
SMTP_SERVER = "smtp.yourdomain.com"
SMTP_PORT = 587  # or 465 for SSL
```

## Testing

1. **Start the backend server** (if not running):
   ```powershell
   cd "c:\Users\keerthi\CS622\AI-Hackathon-2025\fraud detection\FraudDetection\backend"
   python loan_api.py
   ```

2. **Open the loan application form**:
   - Navigate to: http://localhost:5001
   - Or open: `backend/index.html` in a browser

3. **Submit a loan application that will be rejected**:
   - Use low values that will trigger rejection:
     - CIBIL Score: 400 (low credit score)
     - Annual Income: 300000
     - Loan Amount: 5000000 (high loan amount)
     - Email: Your actual email address

4. **Check your email inbox**
   - You should receive an email titled: "Loan Application Status - Requires Review"
   - Check spam folder if not in inbox

5. **Check the terminal output**:
   - Look for: `✅ Email sent successfully to your_email@example.com`
   - Or error messages if something went wrong

## Troubleshooting

### Error: "Authentication failed"
- **Cause**: Incorrect email or password
- **Solution**: Double-check credentials, ensure you're using App Password (not regular password)

### Error: "SMTP connection failed"
- **Cause**: Network/firewall blocking SMTP
- **Solution**: Check firewall settings, try different network

### Email not received
- **Check spam folder**
- **Verify email address** was entered correctly in the form
- **Check terminal logs** for error messages
- **Test email server** separately:
  ```python
  import smtplib
  server = smtplib.SMTP("smtp.gmail.com", 587)
  server.starttls()
  server.login("your_email@gmail.com", "your_app_password")
  print("✅ Connection successful!")
  server.quit()
  ```

### No email field in form
- The email field is already added to `backend/index.html` (line 327-328)
- Make sure you're using the updated version

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** instead of hardcoding
3. **Add `.env` to `.gitignore`**:
   ```bash
   echo ".env" >> .gitignore
   ```
4. **Rotate passwords** regularly
5. **Use app-specific passwords** instead of account passwords

## What's Fixed

✅ Email extraction from form data
✅ Proper error handling and logging
✅ Configuration check before sending
✅ Support for environment variables
✅ Detailed email with rejection reasons
✅ Improvement suggestions in email
✅ Response includes email status

## Quick Start Commands

```powershell
# Set environment variables (replace with your credentials)
$env:SENDER_EMAIL="youremail@gmail.com"
$env:SENDER_PASSWORD="your-app-password"

# Navigate to backend
cd "c:\Users\keerthi\CS622\AI-Hackathon-2025\fraud detection\FraudDetection\backend"

# Start the server
python loan_api.py
```

Then open: http://localhost:5001

## Need Help?

Check the terminal output for detailed error messages. The system will tell you exactly what's wrong:
- ⚠️ Email not configured
- ⚠️ No email address provided
- ❌ Failed to send email: [error details]
- ✅ Email sent successfully

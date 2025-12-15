# 🚀 Deployment Guide - AI Loan Approval System

Complete guide for deploying the AI Loan Approval System to production environments.

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure:

- [ ] Model training completed (`loan_model.pkl` exists)
- [ ] All tests pass (see `TESTING_GUIDE.md`)
- [ ] Email configured in `rejection_handler.py` (if using emails)
- [ ] Database schema verified
- [ ] API runs locally without errors
- [ ] Web UI displays correctly
- [ ] All dependencies in `requirements.txt`
- [ ] Documentation reviewed

---

## 🏠 Option 1: Local Deployment (Development)

### Setup
```powershell
cd "fraud detection\FraudDetection\backend"
pip install -r requirements.txt
python train_loan_model.py
python loan_api.py
```

### Access
- Web UI: `http://localhost:5001`
- API: `http://localhost:5001/predict`

### Use Case
- Development and testing
- Demonstration and demos
- Small-scale internal use

---

## 🖥️ Option 2: Windows Server Deployment

### 1. Install Python on Server
```powershell
# Download and install Python 3.9+ from python.org
# Add to PATH during installation
```

### 2. Clone/Copy Project
```powershell
# Copy project to server
# Example: C:\ai-loan-approval\
```

### 3. Install Dependencies
```powershell
cd C:\ai-loan-approval\backend
pip install -r requirements.txt
```

### 4. Create Windows Service (Optional)
```powershell
# Using NSSM (Non-Sucking Service Manager)
# Download from: https://nssm.cc/download

nssm install LoanApprovalAPI "C:\Python39\python.exe" "C:\ai-loan-approval\backend\loan_api.py"
nssm start LoanApprovalAPI
```

### 5. Configure Firewall
```powershell
# Allow port 5001 through Windows Firewall
New-NetFirewallRule -DisplayName "Loan Approval API" `
    -Direction Inbound -Action Allow -Protocol TCP -LocalPort 5001
```

### 6. Access
- Web UI: `http://<server-ip>:5001`
- API: `http://<server-ip>:5001/predict`

---

## ☁️ Option 3: Azure App Service Deployment

### 1. Create App Service
```powershell
# Login to Azure
az login

# Create resource group
az group create --name loanapproval-rg --location eastus

# Create App Service plan
az appservice plan create --name loanapproval-plan `
    --resource-group loanapproval-rg --sku F1 --is-linux

# Create web app
az webapp create --resource-group loanapproval-rg `
    --plan loanapproval-plan --name loanapprovalapp --runtime "PYTHON|3.9"
```

### 2. Deploy Application
```powershell
# Navigate to project directory
cd fraud detection\FraudDetection\backend

# Create deployment package
Compress-Archive -Path * -DestinationPath app.zip

# Deploy to Azure
az webapp deployment source config-zip --resource-group loanapproval-rg `
    --name loanapprovalapp --src app.zip
```

### 3. Configure Environment Variables
```powershell
# Set SMTP credentials
az webapp config appsettings set --resource-group loanapproval-rg `
    --name loanapprovalapp `
    --settings SENDER_EMAIL="your_email@gmail.com" `
    SENDER_PASSWORD="your_app_password"
```

### 4. Access
- Web UI: `https://loanapprovalapp.azurewebsites.net`
- API: `https://loanapprovalapp.azurewebsites.net/predict`

---

## 🐳 Option 4: Docker Deployment

### 1. Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5001/health')"

# Run application
CMD ["python", "loan_api.py"]
```

### 2. Create docker-compose.yml
```yaml
version: '3.8'

services:
  loan-approval-api:
    build: ./backend
    ports:
      - "5001:5001"
    environment:
      - SENDER_EMAIL=your_email@gmail.com
      - SENDER_PASSWORD=your_app_password
    volumes:
      - ./backend/rejected_applications.db:/app/rejected_applications.db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 3. Build and Run
```bash
# Build image
docker build -t loan-approval-api ./backend

# Run container
docker run -p 5001:5001 \
  -e SENDER_EMAIL="your_email@gmail.com" \
  -e SENDER_PASSWORD="your_app_password" \
  loan-approval-api

# Or use docker-compose
docker-compose up -d
```

### 4. Access
- Web UI: `http://localhost:5001`
- API: `http://localhost:5001/predict`

---

## ☁️ Option 5: AWS EC2 Deployment

### 1. Launch EC2 Instance
```bash
# Create security group allowing port 5001
aws ec2 create-security-group \
  --group-name loan-approval-sg \
  --description "Security group for Loan Approval API"

aws ec2 authorize-security-group-ingress \
  --group-name loan-approval-sg \
  --protocol tcp --port 5001 --cidr 0.0.0.0/0
```

### 2. Connect and Setup
```bash
# SSH into instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Install Python and dependencies
sudo yum update -y
sudo yum install python3 python3-pip -y

# Clone/download project
git clone <your-repo>
cd fraud detection/FraudDetection/backend

# Install requirements
pip install -r requirements.txt

# Train model (if not pre-trained)
python train_loan_model.py

# Start API with systemd
sudo systemctl restart loan-approval-api
```

### 3. Configure systemd Service
```ini
# /etc/systemd/system/loan-approval-api.service
[Unit]
Description=AI Loan Approval API
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/fraud-detection/backend
ExecStart=/usr/bin/python3 /home/ec2-user/fraud-detection/backend/loan_api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4. Access
- Web UI: `http://<elastic-ip>:5001`
- API: `http://<elastic-ip>:5001/predict`

---

## 🏪 Option 6: Heroku Deployment

### 1. Create Procfile
```
web: python loan_api.py
```

### 2. Create runtime.txt
```
python-3.9.16
```

### 3. Deploy
```bash
# Install Heroku CLI
# Login
heroku login

# Create app
heroku create loan-approval-app

# Set environment variables
heroku config:set SENDER_EMAIL="your_email@gmail.com"
heroku config:set SENDER_PASSWORD="your_app_password"

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

### 4. Access
- Web UI: `https://loan-approval-app.herokuapp.com`
- API: `https://loan-approval-app.herokuapp.com/predict`

---

## 🔐 Production Security Best Practices

### 1. Environment Variables
```powershell
# Never hardcode credentials
# Use environment variables instead

# Example: .env file (DO NOT COMMIT)
SENDER_EMAIL="your_email@gmail.com"
SENDER_PASSWORD="your_app_password"
DATABASE_PATH="/var/lib/loan-approval/rejected_applications.db"
SECRET_KEY="random-secret-key-here"
```

### 2. Use Production WSGI Server
```bash
# Replace Flask development server with Gunicorn

pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 loan_api:app

# Or use uWSGI
pip install uwsgi
uwsgi --http :5001 --wsgi-file loan_api.py --callable app
```

### 3. Enable HTTPS
```bash
# Use Let's Encrypt for free SSL certificate
# Or configure with your domain provider

# Example with nginx reverse proxy:
# Configure SSL on nginx frontend
# Proxy to Flask backend on localhost:5001
```

### 4. Database Security
```python
# Encrypt database file
# Set proper file permissions
chmod 600 rejected_applications.db

# Regular backups
cp rejected_applications.db /backup/rejected_applications.db.$(date +%Y%m%d)
```

### 5. Rate Limiting
```python
# Add to loan_api.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/predict', methods=['POST'])
@limiter.limit("30 per minute")
def predict():
    # Prediction endpoint
```

### 6. Logging and Monitoring
```python
# Add comprehensive logging
import logging

logging.basicConfig(
    filename='loan_approval.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Log important events
logger.info(f"Prediction made - approved: {approved}")
logger.warning(f"Failed prediction for email: {email}")
logger.error(f"Email sending failed: {error}")
```

---

## 📊 Monitoring & Maintenance

### Key Metrics to Monitor
- **API Response Time** - Target: <200ms
- **Error Rate** - Target: <1%
- **Database Size** - Alert: >1GB
- **Memory Usage** - Alert: >500MB
- **CPU Usage** - Alert: >80%
- **Email Failure Rate** - Target: <5%

### Health Check Setup
```powershell
# Monitor API health
# Run every 5 minutes via cron/scheduler

curl -X GET http://localhost:5001/health

# If returns non-200, alert and restart
if ($lastexitcode -ne 0) {
    Restart-Service LoanApprovalAPI
}
```

### Database Maintenance
```bash
# Regular backups (daily)
0 2 * * * /usr/local/bin/backup_db.sh

# Optimize database (weekly)
0 3 * * 0 sqlite3 /var/lib/loan-approval/rejected_applications.db VACUUM

# Archive old records (monthly)
0 4 1 * * /usr/local/bin/archive_old_rejections.sh
```

---

## 🚨 Troubleshooting Production Issues

### Issue: High Memory Usage
```python
# Add memory profiling
from memory_profiler import profile

@profile
def predict():
    # Check memory usage
    pass

# Solution: Implement model caching, limit batch size
```

### Issue: Slow Database Queries
```python
# Add database indexing
CREATE INDEX idx_rejection_date ON rejected_applications(application_date);
CREATE INDEX idx_email ON rejected_applications(email_address);

# Solution: Add indexes, implement pagination
```

### Issue: Email Sending Failures
```python
# Add retry logic
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential())
def send_rejection_email():
    # Send email with automatic retry
    pass
```

### Issue: API Rate Limiting
```python
# Implement API throttling
from functools import wraps
from time import time

call_times = {}

def rate_limit(max_calls, time_window):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time()
            # Check rate limit
            pass
        return wrapper
    return decorator
```

---

## 📈 Scaling Considerations

### Vertical Scaling (Larger Server)
- More CPU cores
- More RAM (for model caching)
- Larger disk (for database)

### Horizontal Scaling (Multiple Servers)
```yaml
# Load Balancer (nginx)
upstream loan_approval {
    server server1:5001;
    server server2:5001;
    server server3:5001;
}

server {
    location /predict {
        proxy_pass http://loan_approval;
    }
}
```

### Database Scaling
```python
# Implement read replicas
# Archive old records to separate storage
# Consider PostgreSQL for better concurrency
```

---

## 📋 Post-Deployment Verification

After deployment, verify:

- [ ] Web UI loads correctly
- [ ] Health check endpoint responds
- [ ] Predictions return correct format
- [ ] Rejections saved to database
- [ ] Email notifications working (if configured)
- [ ] Admin endpoints accessible
- [ ] Error handling works
- [ ] Performance meets targets (<200ms)
- [ ] Logs are being generated
- [ ] Monitoring is active

---

## 🔄 Continuous Deployment (CI/CD)

### GitHub Actions Example
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Azure
        run: |
          az webapp deployment source config-zip \
            --resource-group loanapproval-rg \
            --name loanapprovalapp \
            --src app.zip
```

---

## 📞 Support & Escalation

### Common Issues

**API not starting:**
- Check Python version (3.8+)
- Verify all dependencies installed
- Check port 5001 not in use

**Model not loading:**
- Verify loan_model.pkl exists
- Check file permissions
- Try retraining model

**Email not sending:**
- Verify Gmail App Password (not regular password)
- Check email configuration in rejection_handler.py
- Test SMTP connection manually

**Database locked:**
- Check for multiple instances running
- Verify file permissions
- Restart service

---

## 🎉 Deployment Checklist

- [ ] Choose deployment option
- [ ] Complete pre-deployment checklist
- [ ] Follow setup steps for chosen option
- [ ] Verify all security best practices
- [ ] Set up monitoring
- [ ] Test all endpoints
- [ ] Configure backups
- [ ] Document deployment details
- [ ] Create incident response plan
- [ ] Train team on operations

---

## 📞 Getting Help

For deployment issues:
1. Check relevant section above
2. Review logs for error messages
3. Consult troubleshooting section
4. Test in development environment first
5. Verify all prerequisites met

---

**Deployment Guide Complete**  
**Ready for Production** ✅

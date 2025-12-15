# Email Setup Script for Loan Application System
# This script helps you configure email notifications

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "    Email Configuration Setup for Loan Application System" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if already configured
$currentEmail = [Environment]::GetEnvironmentVariable("SENDER_EMAIL", "User")
$currentPassword = [Environment]::GetEnvironmentVariable("SENDER_PASSWORD", "User")

if ($currentEmail -and $currentPassword) {
    Write-Host "✅ Email credentials already configured:" -ForegroundColor Green
    Write-Host "   Email: $currentEmail" -ForegroundColor Yellow
    Write-Host ""
    $overwrite = Read-Host "Do you want to update them? (y/n)"
    if ($overwrite -ne 'y') {
        Write-Host "Configuration unchanged." -ForegroundColor Yellow
        exit
    }
}

Write-Host "📧 Email Provider Selection:" -ForegroundColor Cyan
Write-Host "1. Gmail (recommended)"
Write-Host "2. Outlook/Hotmail"
Write-Host "3. Yahoo Mail"
Write-Host "4. Other"
Write-Host ""

$choice = Read-Host "Select provider (1-4)"

# Get email and password
Write-Host ""
$email = Read-Host "Enter your email address"
$password = Read-Host "Enter your App Password (will be hidden)" -AsSecureString
$passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)
)

# Set environment variables for current session
$env:SENDER_EMAIL = $email
$env:SENDER_PASSWORD = $passwordPlain

Write-Host ""
Write-Host "✅ Environment variables set for current session" -ForegroundColor Green
Write-Host ""

# Ask if they want to persist
$persist = Read-Host "Save credentials permanently for this user? (y/n)"
if ($persist -eq 'y') {
    [Environment]::SetEnvironmentVariable("SENDER_EMAIL", $email, "User")
    [Environment]::SetEnvironmentVariable("SENDER_PASSWORD", $passwordPlain, "User")
    Write-Host "✅ Credentials saved permanently" -ForegroundColor Green
} else {
    Write-Host "⚠️  Credentials only set for this session" -ForegroundColor Yellow
    Write-Host "   Run this script again or set manually with:" -ForegroundColor Yellow
    Write-Host '   $env:SENDER_EMAIL="your@email.com"' -ForegroundColor Gray
    Write-Host '   $env:SENDER_PASSWORD="your-app-password"' -ForegroundColor Gray
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Testing email configuration..." -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Test the configuration
python test_email_config.py

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Start the loan API server: python loan_api.py" -ForegroundColor Yellow
Write-Host "2. Open http://localhost:5001 in your browser" -ForegroundColor Yellow
Write-Host "3. Submit a loan application with a valid email" -ForegroundColor Yellow
Write-Host "4. Check your email for rejection notifications" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan

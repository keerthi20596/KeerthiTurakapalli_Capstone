"""
Email Configuration Test Script
Run this to verify your email settings are working correctly
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Load configuration - using Gmail SMTP
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "arthi20244@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "Keerthi@64")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def test_email_config():
    """Test if email credentials are configured"""
    print("=" * 60)
    print("EMAIL CONFIGURATION TEST")
    print("=" * 60)
    
    # Check if configured (looking for placeholder values, not actual configured values)
    if SENDER_EMAIL == "your_email@gmail.com" or SENDER_PASSWORD == "your_app_password":
        print("\n❌ EMAIL NOT CONFIGURED!")
        print("\nPlease configure your email credentials:")
        print("1. Edit rejection_handler.py and set SENDER_EMAIL and SENDER_PASSWORD")
        print("   OR")
        print("2. Set environment variables:")
        print("   PowerShell:")
        print('   $env:SENDER_EMAIL="your_email@gmail.com"')
        print('   $env:SENDER_PASSWORD="your_app_password"')
        print("\nSee EMAIL_SETUP_GUIDE.md for detailed instructions")
        return False
    
    print(f"\n✅ Email configured: {SENDER_EMAIL}")
    print(f"✅ Password configured: {'*' * len(SENDER_PASSWORD)}")
    
    # Test connection
    print(f"\n🔄 Testing connection to {SMTP_SERVER}:{SMTP_PORT}...")
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        print("✅ Connected to SMTP server")
        
        server.starttls()
        print("✅ TLS encryption enabled")
        
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        print("✅ Authentication successful!")
        
        server.quit()
        print("\n" + "=" * 60)
        print("🎉 EMAIL CONFIGURATION IS WORKING!")
        print("=" * 60)
        print("\nYou can now receive rejection emails when loans are rejected.")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("\n❌ AUTHENTICATION FAILED!")
        print("\nPossible reasons:")
        print("1. Incorrect email or password")
        print("2. Using regular password instead of App Password")
        print("3. 2-Step Verification not enabled")
        print("\nFor Gmail:")
        print("- Enable 2-Step Verification: https://myaccount.google.com/security")
        print("- Generate App Password: https://myaccount.google.com/apppasswords")
        return False
        
    except smtplib.SMTPException as e:
        print(f"\n❌ SMTP ERROR: {str(e)}")
        print("\nCheck your SMTP server settings")
        return False
        
    except Exception as e:
        print(f"\n❌ CONNECTION ERROR: {str(e)}")
        print("\nPossible reasons:")
        print("1. No internet connection")
        print("2. Firewall blocking SMTP")
        print("3. Incorrect SMTP server or port")
        return False


def send_test_email():
    """Send a test email"""
    recipient = input("\nEnter email address to send test email to: ").strip()
    
    if not recipient:
        print("❌ No email address provided")
        return
    
    try:
        msg = MIMEMultipart()
        msg['Subject'] = "Test Email - Loan System"
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient
        
        html = """
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #4CAF50;">✅ Email Configuration Test Successful!</h2>
                <p>This is a test email from your Loan Approval System.</p>
                <p>If you received this email, your email notification system is working correctly!</p>
                <hr>
                <p style="color: #999; font-size: 12px;">
                    This is an automated test message from the AI Loan Approval System.
                </p>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        print(f"\n🔄 Sending test email to {recipient}...")
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Test email sent successfully to {recipient}")
        print("📧 Check your inbox (and spam folder)")
        
    except Exception as e:
        print(f"❌ Failed to send test email: {str(e)}")


if __name__ == "__main__":
    success = test_email_config()
    
    if success:
        print("\nWould you like to send a test email? (y/n): ", end="")
        choice = input().strip().lower()
        if choice == 'y':
            send_test_email()
    
    print("\n" + "=" * 60)
    print("For detailed setup instructions, see EMAIL_SETUP_GUIDE.md")
    print("=" * 60)

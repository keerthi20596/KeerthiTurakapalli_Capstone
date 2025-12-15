import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'rejected_applications.db')

# Email configuration - Gmail
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "arthi20244@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "Keerthi@64")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Check if email is configured (check for placeholder values)
EMAIL_CONFIGURED = (SENDER_EMAIL != "your_email@gmail.com" and 
                   SENDER_PASSWORD != "your_app_password" and
                   SENDER_EMAIL and SENDER_PASSWORD)


def init_database():
    """Initialize SQLite database for rejected applications"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rejected_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            applicant_name TEXT,
            income_annum REAL,
            loan_amount REAL,
            loan_term INTEGER,
            cibil_score INTEGER,
            education TEXT,
            self_employed TEXT,
            no_of_dependents INTEGER,
            residential_assets_value REAL,
            commercial_assets_value REAL,
            luxury_assets_value REAL,
            bank_asset_value REAL,
            debt_to_income_ratio REAL,
            rejection_probability REAL,
            rejection_reason TEXT,
            applicant_email TEXT,
            email_sent BOOLEAN DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()


def save_rejected_application(data, probability, applicant_email=None):
    """Save rejected application to database"""
    init_database()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    debt_to_income = (data.get('loan_amount', 0) / data.get('income_annum', 1)) * 100
    
    # Determine rejection reason
    rejection_reason = get_rejection_reason(data, probability)
    
    cursor.execute('''
        INSERT INTO rejected_applications (
            applicant_name, income_annum, loan_amount, loan_term, cibil_score,
            education, self_employed, no_of_dependents, residential_assets_value,
            commercial_assets_value, luxury_assets_value, bank_asset_value,
            debt_to_income_ratio, rejection_probability, rejection_reason, applicant_email
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('applicant_name', 'Unknown'),
        data.get('income_annum'),
        data.get('loan_amount'),
        data.get('loan_term'),
        data.get('cibil_score'),
        data.get('education'),
        data.get('self_employed'),
        data.get('no_of_dependents'),
        data.get('residential_assets_value'),
        data.get('commercial_assets_value'),
        data.get('luxury_assets_value'),
        data.get('bank_asset_value'),
        debt_to_income,
        probability,
        rejection_reason,
        applicant_email
    ))
    
    conn.commit()
    conn.close()


def get_rejection_reason(data, probability):
    """Generate reason for rejection based on financial metrics"""
    reasons = []
    
    cibil_score = data.get('cibil_score', 0)
    if cibil_score < 500:
        reasons.append("Low credit score (below 500)")
    elif cibil_score < 650:
        reasons.append("Below-average credit score")
    
    debt_to_income = (data.get('loan_amount', 0) / data.get('income_annum', 1)) * 100
    if debt_to_income > 50:
        reasons.append(f"High debt-to-income ratio ({debt_to_income:.1f}%)")
    
    total_assets = (data.get('residential_assets_value', 0) + 
                   data.get('commercial_assets_value', 0) + 
                   data.get('luxury_assets_value', 0) + 
                   data.get('bank_asset_value', 0))
    
    if total_assets < 500000:
        reasons.append("Limited asset base for collateral")
    
    if data.get('self_employed') == 'Yes':
        reasons.append("Self-employment status may indicate income volatility")
    
    if data.get('no_of_dependents', 0) > 4:
        reasons.append("High number of dependents may affect repayment capacity")
    
    return "; ".join(reasons) if reasons else "Insufficient financial credentials"


def save_email_to_file(applicant_name, applicant_email, data, probability):
    """Save email content to file (TEST MODE)"""
    try:
        log_file = os.path.join(os.path.dirname(__file__), 'rejection_emails.log')
        
        debt_to_income = (data.get('loan_amount', 0) / data.get('income_annum', 1)) * 100
        total_assets = (data.get('residential_assets_value', 0) + 
                       data.get('commercial_assets_value', 0) + 
                       data.get('luxury_assets_value', 0) + 
                       data.get('bank_asset_value', 0))
        
        rejection_reason = get_rejection_reason(data, probability)
        suggestions = get_improvement_suggestions(data)
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*70}\n")
            f.write(f"REJECTION EMAIL - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*70}\n")
            f.write(f"TO: {applicant_email}\n")
            f.write(f"FROM: {SENDER_EMAIL}\n")
            f.write(f"NAME: {applicant_name}\n")
            f.write(f"SUBJECT: Loan Application Status - Requires Review\n")
            f.write(f"\n--- APPLICATION DETAILS ---\n")
            f.write(f"Annual Income: ${data.get('income_annum', 0):,.0f}\n")
            f.write(f"Loan Amount: ${data.get('loan_amount', 0):,.0f}\n")
            f.write(f"Debt-to-Income Ratio: {debt_to_income:.1f}%\n")
            f.write(f"CIBIL Score: {data.get('cibil_score', 0)}\n")
            f.write(f"Total Assets: ${total_assets:,.0f}\n")
            f.write(f"Risk Score: {probability*100:.1f}%\n")
            f.write(f"\n--- REJECTION REASON ---\n")
            f.write(f"{rejection_reason}\n")
            f.write(f"\n--- EMAIL BODY PREVIEW ---\n")
            f.write(f"Dear {applicant_name},\n\n")
            f.write(f"Thank you for applying for a loan. After analyzing your application,\n")
            f.write(f"we regret to inform you that it does not meet our approval criteria.\n\n")
            f.write(f"Reasons: {rejection_reason}\n\n")
            f.write(f"✅ EMAIL NOTIFICATION TRIGGERED SUCCESSFULLY\n")
            f.write(f"{'='*70}\n\n")
        
        print(f"✅ Email notification logged to: {log_file}")
        print(f"📧 Email would be sent to: {applicant_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to log email: {str(e)}")
        return False


def send_rejection_email(applicant_name, applicant_email, data, probability):
    """Send rejection notification email"""
    if not applicant_email:
        print("⚠️ No email address provided. Skipping email notification.")
        return False
    
    # TEST MODE: Save email to file instead of sending (for Microsoft 365 setup issues)
    TEST_MODE = os.getenv("EMAIL_TEST_MODE", "true").lower() == "true"
    
    if TEST_MODE:
        print(f"📧 TEST MODE: Email would be sent to {applicant_email}")
        print("   (Email content will be saved to rejection_emails.log)")
        return save_email_to_file(applicant_name, applicant_email, data, probability)
    
    if not EMAIL_CONFIGURED:
        print("⚠️ Email not configured! Please set SENDER_EMAIL and SENDER_PASSWORD")
        print("   Either edit rejection_handler.py or set environment variables:")
        print("   - SENDER_EMAIL=your_email@gmail.com")
        print("   - SENDER_PASSWORD=your_app_password")
        print("\n💡 TIP: Set EMAIL_TEST_MODE=false to disable test mode")
        return False
    
    try:
        # Calculate metrics for email
        debt_to_income = (data.get('loan_amount', 0) / data.get('income_annum', 1)) * 100
        total_assets = (data.get('residential_assets_value', 0) + 
                       data.get('commercial_assets_value', 0) + 
                       data.get('luxury_assets_value', 0) + 
                       data.get('bank_asset_value', 0))
        
        rejection_reason = get_rejection_reason(data, probability)
        
        # Generate suggestions
        suggestions = get_improvement_suggestions(data)
        
        # Create email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Loan Application Status - Requires Review"
        msg['From'] = SENDER_EMAIL
        msg['To'] = applicant_email
        
        # HTML email body
        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #f44336; color: white; padding: 20px; border-radius: 5px; text-align: center; }}
                    .content {{ padding: 20px; background: #f9f9f9; margin: 20px 0; border-radius: 5px; }}
                    .section {{ margin: 20px 0; }}
                    .section h3 {{ color: #d32f2f; margin-bottom: 10px; }}
                    .metric {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #ddd; }}
                    .suggestion {{ background: #e3f2fd; padding: 12px; margin: 8px 0; border-left: 4px solid #2196f3; border-radius: 3px; }}
                    .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>Loan Application Status</h2>
                        <p>⚠️ Application Requires Further Review</p>
                    </div>
                    
                    <div class="content">
                        <p>Dear {applicant_name},</p>
                        
                        <p>Thank you for applying for a loan with us. We appreciate the opportunity to review your application.</p>
                        
                        <p>After careful analysis of your financial profile using our AI assessment system, we regret to inform you that your current application does not meet our approval criteria at this time.</p>
                        
                        <div class="section">
                            <h3>📊 Application Analysis</h3>
                            <div class="metric">
                                <span>Annual Income:</span>
                                <strong>${data.get('income_annum', 0):,.0f}</strong>
                            </div>
                            <div class="metric">
                                <span>Requested Loan Amount:</span>
                                <strong>${data.get('loan_amount', 0):,.0f}</strong>
                            </div>
                            <div class="metric">
                                <span>Debt-to-Income Ratio:</span>
                                <strong>{debt_to_income:.1f}%</strong>
                            </div>
                            <div class="metric">
                                <span>Credit Score (CIBIL):</span>
                                <strong>{data.get('cibil_score', 0)}</strong>
                            </div>
                            <div class="metric">
                                <span>Total Assets:</span>
                                <strong>${total_assets:,.0f}</strong>
                            </div>
                            <div class="metric">
                                <span>Risk Assessment Confidence:</span>
                                <strong>{probability*100:.1f}%</strong>
                            </div>
                        </div>
                        
                        <div class="section">
                            <h3>❌ Reason for Review</h3>
                            <p>{rejection_reason}</p>
                        </div>
                        
                        <div class="section">
                            <h3>✅ How to Improve Your Application</h3>
                            {suggestions}
                        </div>
                        
                        <div class="section">
                            <p><strong>Next Steps:</strong></p>
                            <ul>
                                <li>Review the suggestions above to strengthen your financial profile</li>
                                <li>Reapply after 3-6 months with improved metrics</li>
                                <li>Contact our loan officer for personalized guidance</li>
                                <li>Consider alternative loan amounts or terms</li>
                            </ul>
                        </div>
                        
                        <p>We encourage you to reapply once you've addressed the above areas. Our team is here to help you achieve your financial goals.</p>
                        
                        <p>Best regards,<br>
                        <strong>AI Loan Assessment Team</strong><br>
                        Your Financial Partner</p>
                    </div>
                    
                    <div class="footer">
                        <p>This is an automated message. Please do not reply to this email.</p>
                        <p>For assistance, contact our loan department at support@loanapproval.com</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Email sent successfully to {applicant_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        print("⚠️  Make sure to configure SENDER_EMAIL and SENDER_PASSWORD in rejection_handler.py")
        return False


def get_improvement_suggestions(data):
    """Generate HTML suggestions for improving application"""
    suggestions_html = ""
    
    cibil_score = data.get('cibil_score', 0)
    if cibil_score < 650:
        suggestions_html += f"""
        <div class="suggestion">
            <strong>📈 Improve Credit Score</strong><br>
            Your current CIBIL score is {cibil_score}. We recommend aiming for 700+.
            <ul>
                <li>Pay all bills on time</li>
                <li>Reduce credit utilization</li>
                <li>Clear outstanding debts</li>
                <li>Check credit report for errors</li>
            </ul>
        </div>
        """
    
    debt_to_income = (data.get('loan_amount', 0) / data.get('income_annum', 1)) * 100
    if debt_to_income > 40:
        max_recommended = int(data.get('income_annum', 0) * 0.4)
        suggestions_html += f"""
        <div class="suggestion">
            <strong>💰 Reduce Loan Amount</strong><br>
            Your debt-to-income ratio is {debt_to_income:.1f}%. Recommended maximum: ${max_recommended:,.0f}
            <ul>
                <li>Lower your requested loan amount</li>
                <li>Increase income sources</li>
                <li>Wait for salary increments</li>
            </ul>
        </div>
        """
    
    total_assets = (data.get('residential_assets_value', 0) + 
                   data.get('commercial_assets_value', 0) + 
                   data.get('luxury_assets_value', 0) + 
                   data.get('bank_asset_value', 0))
    
    if total_assets < 1000000:
        suggestions_html += f"""
        <div class="suggestion">
            <strong>🏠 Build Asset Base</strong><br>
            Current total assets: ${total_assets:,.0f}
            <ul>
                <li>Increase savings</li>
                <li>Invest in property or assets</li>
                <li>Accumulate collateral</li>
            </ul>
        </div>
        """
    
    if data.get('self_employed') == 'Yes':
        suggestions_html += f"""
        <div class="suggestion">
            <strong>📋 Document Income Stability</strong><br>
            Self-employed applicants should provide:
            <ul>
                <li>2-3 years of tax returns</li>
                <li>Bank statements showing consistent income</li>
                <li>Business registration documents</li>
                <li>Financial statements</li>
            </ul>
        </div>
        """
    
    if not suggestions_html:
        suggestions_html = """
        <div class="suggestion">
            <strong>📞 Contact Our Loan Officer</strong><br>
            Your profile is complex. Let us review it manually to find suitable options.
        </div>
        """
    
    return suggestions_html


def get_rejected_applications():
    """Retrieve all rejected applications from database"""
    init_database()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM rejected_applications ORDER BY application_date DESC')
    applications = cursor.fetchall()
    conn.close()
    
    return [dict(app) for app in applications]


def get_rejection_stats():
    """Get statistics about rejected applications"""
    init_database()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as total FROM rejected_applications')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) as emailed FROM rejected_applications WHERE email_sent = 1')
    emailed = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(cibil_score) as avg_score FROM rejected_applications')
    avg_score = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(debt_to_income_ratio) as avg_dti FROM rejected_applications')
    avg_dti = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total_rejected': total,
        'emails_sent': emailed,
        'avg_credit_score': avg_score,
        'avg_debt_to_income': avg_dti
    }

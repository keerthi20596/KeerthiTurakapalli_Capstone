import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'rejected_applications.db')

if not os.path.exists(db_path):
    print("❌ Database does not exist yet")
else:
    print(f"✅ Database location: {db_path}\n")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM rejected_applications')
    total = cursor.fetchone()[0]
    print(f"📊 Total rejected applications: {total}\n")
    
    if total > 0:
        cursor.execute('''
            SELECT id, application_date, applicant_name, applicant_email, 
                   cibil_score, income_annum, loan_amount, loan_term,
                   debt_to_income_ratio, rejection_probability, rejection_reason,
                   email_sent
            FROM rejected_applications 
            ORDER BY application_date DESC 
            LIMIT 10
        ''')
        
        print("=" * 100)
        print("REJECTED LOAN APPLICATIONS")
        print("=" * 100)
        
        for row in cursor.fetchall():
            print(f"\n📋 Application ID: {row[0]}")
            print(f"📅 Date: {row[1]}")
            print(f"👤 Applicant: {row[2] or 'N/A'}")
            print(f"📧 Email: {row[3] or 'N/A'}")
            print(f"💳 CIBIL Score: {row[4]}")
            print(f"💰 Annual Income: ${row[5]:,.0f}")
            print(f"🏦 Loan Amount: ${row[6]:,.0f}")
            print(f"📆 Loan Term: {row[7]} months")
            print(f"📊 Debt-to-Income Ratio: {row[8]:.1f}%")
            print(f"⚠️  Rejection Risk: {row[9]*100:.1f}%")
            print(f"❌ Reason: {row[10]}")
            print(f"✉️  Email Sent: {'Yes' if row[11] else 'No'}")
            print("-" * 100)
        
        print("\n" + "=" * 100)
        print(f"Total Records: {total}")
        print("=" * 100)
    
    conn.close()

import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'rejected_applications.db')

if not os.path.exists(db_path):
    print("❌ Database does not exist")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get count before deletion
    cursor.execute('SELECT COUNT(*) FROM rejected_applications')
    count_before = cursor.fetchone()[0]
    
    # Delete all records
    cursor.execute('DELETE FROM rejected_applications')
    conn.commit()
    
    # Verify deletion
    cursor.execute('SELECT COUNT(*) FROM rejected_applications')
    count_after = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"✅ Database cleared!")
    print(f"📊 Records deleted: {count_before}")
    print(f"📊 Records remaining: {count_after}")
    print(f"\nThe table is now empty and ready for new rejections.")

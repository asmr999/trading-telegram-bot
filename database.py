import sqlite3
import os

# دالة لإنشاء اتصال بقاعدة البيانات
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# إنشاء الجداول تلقائياً إذا لم تكن موجودة عند تشغيل البوت
try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            status TEXT DEFAULT 'pending',
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized successfully.")
except Exception as e:
    print(f"Database initialization error: {e}")

# دالة لإضافة مستخدم جديد (تستخدم عند الضغط على أزرار البوت)
def add_user(user_id, username=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error in add_user: {e}")
        return False

# دالة للتحقق من وجود المستخدم
def check_user(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user
    except Exception as e:
        print(f"Error in check_user: {e}")
        return None

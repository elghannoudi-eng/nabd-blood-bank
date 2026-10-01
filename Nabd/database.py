import sqlite3

DB_NAME = 'nabd_system.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. جدول المتبرعين (محدث بالبيانات الشخصية والتحاليل والمواعيد)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            donor_number TEXT UNIQUE,
            national_id TEXT,
            full_name TEXT,
            phone TEXT,
            whatsapp TEXT,
            age INTEGER,
            gender TEXT,
            address TEXT,
            blood_type TEXT,
            blood_type_verified BOOLEAN DEFAULT 0,
            verified_by_staff TEXT,
            weight TEXT,
            height TEXT,
            blood_pressure TEXT,
            lab_results TEXT,
            virus_status TEXT DEFAULT 'سليم',
            last_donation_date TEXT,
            next_donation_date TEXT,
            donation_completed BOOLEAN DEFAULT 1,
            password TEXT,
            qr_code TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. جدول الكادر الطبي والمسؤولين
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medical_staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_code TEXT UNIQUE,
            full_name TEXT,
            specialty TEXT,
            workplace TEXT,
            phone TEXT,
            whatsapp TEXT,
            role TEXT DEFAULT 'staff', -- 'staff' أو 'admin' للمسؤول
            password TEXT
        )
    ''')
    
    # 3. جدول الإعلانات ونداءات التبرع
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            blood_type_needed TEXT,
            urgency_level TEXT, -- 'عاجل' أو 'عادي'
            units_required INTEGER,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 4. جدول سجلات العمليات والتوثيق
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medical_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER,
            donor_id INTEGER,
            action_details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # إضافة حساب المسؤول الرئيسي الافتراضي (Admin) إذا لم يكن موجوداً
    cursor.execute("SELECT COUNT(*) FROM medical_staff WHERE role = 'admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO medical_staff (staff_code, full_name, specialty, workplace, phone, whatsapp, role, password) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ('ADM-001', 'أحمد الغنودي (المسؤول)', 'إدارة النظام والتحكم', 'مصرف الدم المركزي - صبراتة', '0910000000', '0910000000', 'admin', '1234'))

    # إضافة عنصر طبي افتراضي
    cursor.execute("SELECT COUNT(*) FROM medical_staff WHERE role = 'staff'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO medical_staff (staff_code, full_name, specialty, workplace, phone, whatsapp, role, password) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ('MED-101', 'د. محمد الطبيب', 'فحص وتحاليل', 'مصرف الدم المركزي - صبراتة', '0920000000', '0920000000', 'staff', '1234'))
    
    conn.commit()
    conn.close()
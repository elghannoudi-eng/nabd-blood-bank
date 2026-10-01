import sqlite3

def create_admin_account():
    conn = sqlite3.connect('nabd.db')
    cursor = conn.cursor()
    
    # التأكد من وجود الجدول بالهيكلة الصحيحة
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medical_staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_code TEXT,
            full_name TEXT,
            specialty TEXT,
            workplace TEXT,
            phone TEXT,
            whatsapp TEXT,
            role TEXT DEFAULT 'staff',
            password TEXT
        )
    ''')
    
    # حذف أي حساب مسجل مسبقاً بنفس رقم الهاتف لمنع التكرار
    cursor.execute("DELETE FROM medical_staff WHERE phone = '0910000000' OR role = 'admin'")
    
    # إدخال حساب المسؤول (المشرف) ببيانات جاهزة ودقيقة
    cursor.execute('''
        INSERT INTO medical_staff (staff_code, full_name, workplace, phone, role, password)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ('ADMIN-01', 'أحمد الغنودي', 'مصرف الدم المركزي صبراتة', '0910000000', 'admin', '123456'))
    
    conn.commit()
    conn.close()
    print("تم إنشاء حساب المسؤول بنجاح!")

if __name__ == '__main__':
    create_admin_account()
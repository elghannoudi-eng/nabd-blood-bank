# server.py - نقطة التشغيل المركزية لنظام نَبض
import os
from flask import Flask
from database import init_db
from routes.main_routes import main_bp
from routes.donor_routes import donor_bp
from routes.staff_routes import staff_bp
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp

app = Flask(__name__)
app.secret_key = 'nabd_secret_key_2026'

# تهيئة قاعدة البيانات والجداول عند الإقلاع
init_db()

# تسجيل الـ Blueprints مع الروابط الخاصة بكل قسم (URLs)
app.register_blueprint(main_bp)
app.register_blueprint(donor_bp, url_prefix='/donor')    # تم إضافة رابط المتبرعين
app.register_blueprint(staff_bp, url_prefix='/staff')    # تم إضافة رابط الكادر الطبي
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')    # تم إضافة رابط لوحة الإدارة

if __name__ == '__main__':
    print("==================================================")
    print("    خادم تطبيق 'نَبض' (الهندسة المعيارية) يعمل الآن    ")
    print("    رابط التشغيل المحلي: http://127.0.0.1:5000         ")
    print("==================================================")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', debug=False, port=port)
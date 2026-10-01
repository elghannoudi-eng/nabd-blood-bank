from flask import Blueprint, render_template_string, request, redirect, url_for, session, flash
from database import get_db_connection
from templates_helper import render_main_page

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. البحث في جدول الكادر الطبي والمسؤولين
        cursor.execute("SELECT * FROM medical_staff WHERE phone = ? AND password = ?", (phone, password))
        staff_user = cursor.fetchone()
        
        if staff_user:
            session['user_id'] = staff_user['id']
            session['user_name'] = staff_user['full_name']
            session['role'] = staff_user['role'] # 'admin' أو 'staff'
            conn.close()
            
            # التوجيه المباشر لتجنب أي خطأ في مسارات الـ Blueprint
            if staff_user['role'] == 'admin':
                return redirect('/admin/dashboard')
            else:
                return redirect('/staff/dashboard')
        
        # 2. البحث في جدول المتبرعين
        cursor.execute("SELECT * FROM donors WHERE phone = ? AND password = ?", (phone, password))
        donor_user = cursor.fetchone()
        
        if donor_user:
            session['user_id'] = donor_user['id']
            session['user_name'] = donor_user['full_name']
            session['role'] = 'donor'
            conn.close()
            return redirect('/donor/profile')
            
        conn.close()
        flash('رقم الهاتف أو الرقم السري غير صحيح!', 'error')
        
    body = '''
    <div class="card" style="max-width: 450px; margin: 0 auto;">
        <h2 style="color: #9a0007; text-align: center; margin-top: 0;">🔐 تسجيل الدخول للنظام</h2>
        <p style="text-align: center; color: #666; font-size: 14px;">أدخل رقم الهاتف والرقم السري الخاص بك للمتابعة</p>
        
        <form method="POST" style="margin-top: 20px;">
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px; font-weight: bold;">رقم الهاتف:</label>
                <input type="text" name="phone" required placeholder="مثال: 0910000000" style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box;">
            </div>
            
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px; font-weight: bold;">الرقم السري:</label>
                <input type="password" name="password" required placeholder="أدخل الرقم السري" style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box;">
            </div>
            
            <div style="margin-bottom: 20px; text-align: left;">
                <a href="/forgot-password" style="color: #d32f2f; font-size: 13px; text-decoration: none;">نسيت الرقم السري؟</a>
            </div>
            
            <button type="submit" class="btn" style="width: 100%; padding: 12px; font-size: 16px;">دخول</button>
        </form>
    </div>
    '''
    return render_main_page(body)

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        phone = request.form.get('phone')
        flash(f'تم إرسال رابط ورقم سري مؤقت عبر الواتساب للرقم: {phone}', 'success')
        return redirect(url_for('auth.login'))
        
    body = '''
    <div class="card" style="max-width: 450px; margin: 0 auto;">
        <h2 style="color: #9a0007; text-align: center; margin-top: 0;">🔑 استعادة الرقم السري</h2>
        <p style="text-align: center; color: #666; font-size: 14px;">أدخل رقم هاتفك المسجل لنرسل لك كلمة مرور مؤقتة عبر الواتساب</p>
        
        <form method="POST" style="margin-top: 20px;">
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px; font-weight: bold;">رقم الهاتف:</label>
                <input type="text" name="phone" required placeholder="مثال: 091xxxxxxx" style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box;">
            </div>
            
            <button type="submit" class="btn" style="width: 100%; padding: 12px; font-size: 16px;">إرسال عبر الواتساب</button>
        </form>
        <div style="text-align: center; margin-top: 15px;">
            <a href="/login" style="color: #555; font-size: 14px;">العودة لتسجيل الدخول</a>
        </div>
    </div>
    '''
    return render_main_page(body)

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')
from flask import Blueprint, render_template_string, session, redirect, url_for, request, flash
from database import get_db_connection
from templates_helper import render_main_page
import random

donor_bp = Blueprint('donor', __name__, url_prefix='/donor')

@donor_bp.route('/profile')
def profile():
    if 'user_id' not in session or session.get('role') != 'donor':
        return redirect(url_for('auth.login'))
        
    donor_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM donors WHERE id = ?", (donor_id,))
    donor = cursor.fetchone()
    conn.close()
    
    if not donor:
        return redirect(url_for('auth.login'))

    completion_status = "مكتمل بنجاح" if donor['donation_completed'] else "غير مكتمل"
    completion_badge_color = "#388e3c" if donor['donation_completed'] else "#d32f2f"
    verified_badge = '<span style="color: #388e3c; font-size: 14px;">✔ تم التأكد</span>' if donor['blood_type_verified'] else '<span style="color: #f57c00; font-size: 14px;">⏳ بانتظار التأكد الطبي</span>'

    body = f'''
    <div class="card" style="max-width: 700px; margin: 0 auto;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #d32f2f; padding-bottom: 12px; margin-bottom: 20px;">
            <h2 style="color: #9a0007; margin: 0;">👤 ملف المتبرع الشخصي</h2>
            <a href="/logout" class="btn" style="background: #d32f2f; padding: 6px 15px; font-size: 14px;">تسجيل الخروج</a>
        </div>

        <div style="display: flex; gap: 20px; align-items: center; background: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <div style="flex-grow: 1;">
                <h3 style="margin: 0 0 5px 0; color: #333;">{donor['full_name']}</h3>
                <p style="margin: 3px 0; color: #666; font-size: 14px;">رقم المتبرع: <strong>{donor['donor_number']}</strong></p>
                <p style="margin: 3px 0; color: #666; font-size: 14px;">الرقم الوطني: {donor['national_id'] or 'غير متوفر'}</p>
            </div>
            <div style="text-align: center; background: #fff; padding: 10px; border: 1px solid #ddd; border-radius: 6px;">
                <p style="margin: 0 0 5px 0; font-size: 11px; color: #555;">QR Code الملف</p>
                <div style="font-size: 24px; font-weight: bold; color: #9a0007;">[{donor['donor_number']}]</div>
            </div>
        </div>

        <h4 style="color: #444; border-bottom: 1px solid #ddd; padding-bottom: 5px;">📋 البيانات الشخصية</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 15px; margin-bottom: 20px;">
            <div>📱 الهاتف: <strong>{donor['phone']}</strong></div>
            <div>💬 الواتساب: <strong>{donor['whatsapp'] or donor['phone']}</strong></div>
            <div> 📍 السكن: <strong>{donor['address'] or 'غير محدد'}</strong></div>
            <div> 🩸 فصيلة الدم: <strong style="color: #9a0007; font-size: 18px;">{donor['blood_type'] or 'غير محددة'}</strong> {verified_badge}</div>
        </div>

        <h4 style="color: #444; border-bottom: 1px solid #ddd; padding-bottom: 5px;">🩺 القياسات والنتائج الطبية</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 15px; margin-bottom: 20px; background: #fff8e1; padding: 12px; border-radius: 6px;">
            <div>⚖️ الوزن: <strong>{donor['weight'] or '--'} كغ</strong></div>
            <div>📏 الطول: <strong>{donor['height'] or '--'} سم</strong></div>
            <div> ضغط الدم: <strong>{donor['blood_pressure'] or '--'}</strong></div>
            <div> حالة الفيروسات: <strong style="color: #388e3c;">{donor['virus_status']}</strong></div>
            <div style="grid-column: span 2;"> ملاحظات طبية: <strong>{donor['lab_results'] or 'لا توجد ملاحظات حالياً'}</strong></div>
        </div>

        <h4 style="color: #444; border-bottom: 1px solid #ddd; padding-bottom: 5px;">📅 سجل التبرعات والمواعيد</h4>
        <div style="font-size: 15px; line-height: 1.8;">
            <div>🕒 تاريخ آخر تبرع: <strong>{donor['last_donation_date'] or 'لا يوجد تبرع سابق'}</strong></div>
            <div>حالة آخر تبرع: <strong style="color: {completion_badge_color};">{completion_status}</strong></div>
            <div>⏳ موعد التبرع القادم: <strong style="color: #1976d2;">{donor['next_donation_date'] or 'متاح للتبرع في أي وقت'}</strong></div>
        </div>
    </div>
    '''
    return render_main_page(body)

@donor_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        password = request.form.get('password')
        blood_type = request.form.get('blood_type')
        national_id = request.form.get('national_id')
        address = request.form.get('address')
        
        donor_number = f"DN-{random.randint(1000, 9999)}"
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO donors (donor_number, full_name, phone, password, blood_type, national_id, address)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (donor_number, full_name, phone, password, blood_type, national_id, address))
            conn.commit()
            conn.close()
            flash('تم تسجيل المتبرع بنجاح!', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            conn.close()
            print("========================================")
            print("REGISTRATION ERROR:", str(e))
            print("========================================")
            flash(f'حدث خطأ أثناء التسجيل: {e}', 'error')

    body = '''
    <div class="card" style="max-width: 500px; margin: 0 auto;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <h2 style="color: #9a0007; margin: 0;">🩸 تسجيل متبرع جديد</h2>
            <a href="/login" style="background: #6c757d; color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; font-size: 14px;">← رجوع للدخول</a>
        </div>
        <form method="POST" style="margin-top: 10px;">
            <div style="margin-bottom: 12px;">
                <label style="display: block; margin-bottom: 5px; font-weight: bold;">الاسم الكامل:</label>
                <input type="text" name="full_name" required placeholder="أدخل الاسم الكامل" style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box;">
            </div>
            <div style="margin-bottom: 12px;">
                <label style="display: block; margin-bottom: 5px; font-weight: bold;">رقم الهاتف:</label>
                <input type="text" name="phone" required placeholder="091xxxxxxx" style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box;">
            </div>
            <div style="margin-bottom: 12px;">
                <label style="display: block; margin-bottom: 5px; font-weight: bold;">الرقم السري للدخول:</label>
                <input type="password" name="password" required placeholder="أدخل الرقم السري الخاص بك" style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box;">
            </div>
            <div style="margin-bottom: 12px;">
                <label style="display: block; margin-bottom: 5px; font-weight: bold;">فصيلة الدم:</label>
                <select name="blood_type" style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box;">
                    <option value="A+">A+</option>
                    <option value="A-">A-</option>
                    <option value="B+">B+</option>
                    <option value="B-">B-</option>
                    <option value="AB+">AB+</option>
                    <option value="AB-">AB-</option>
                    <option value="O+">O+</option>
                    <option value="O-">O-</option>
                </select>
            </div>
            <div style="margin-bottom: 12px;">
                <label style="display: block; margin-bottom: 5px; font-weight: bold;">الرقم الوطني:</label>
                <input type="text" name="national_id" placeholder="الرقم الوطني (اختياري)" style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box;">
            </div>
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px; font-weight: bold;">العنوان (المنطقة):</label>
                <input type="text" name="address" placeholder="مثال: صبراتة - تليل" style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box;">
            </div>
            <button type="submit" class="btn" style="width: 100%; padding: 12px; font-size: 16px; background-color: #9a0007; color: white; border: none; border-radius: 6px; cursor: pointer;">إتمام التسجيل</button>
        </form>
    </div>
    '''
    return render_main_page(body)
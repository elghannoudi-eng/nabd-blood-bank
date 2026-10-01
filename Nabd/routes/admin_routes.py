from flask import Blueprint, render_template_string, request, session, redirect, url_for, flash
from database import get_db_connection
from templates_helper import render_main_page

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # إحصائيات سريعة
    cursor.execute("SELECT COUNT(*) FROM donors")
    total_donors = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM medical_staff WHERE role = 'staff'")
    total_staff = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM announcements WHERE is_active = 1")
    active_announcements = cursor.fetchone()[0]
    
    conn.close()

    body = f'''
    <div class="card" style="max-width: 900px; margin: 0 auto;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #d32f2f; padding-bottom: 12px; margin-bottom: 20px;">
            <h2 style="color: #9a0007; margin: 0;">⚙️ لوحة تحكم المسؤول (Admin Panel)</h2>
            <a href="/logout" class="btn" style="background: #d32f2f; padding: 6px 15px; font-size: 14px;">تسجيل الخروج</a>
        </div>

        <!-- بطاقات الإحصائيات السريعة -->
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 25px; text-align: center;">
            <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; border: 1px solid #bbdefb;">
                <h3 style="margin: 0; color: #1565c0; font-size: 24px;">{total_donors}</h3>
                <p style="margin: 5px 0 0 0; color: #555; font-size: 14px;">إجمالي المتبرعين</p>
            </div>
            <div style="background: #e8f5e9; padding: 15px; border-radius: 8px; border: 1px solid #c8e6c9;">
                <h3 style="margin: 0; color: #2e7d32; font-size: 24px;">{total_staff}</h3>
                <p style="margin: 5px 0 0 0; color: #555; font-size: 14px;">العناصر الطبية</p>
            </div>
            <div style="background: #fff8e1; padding: 15px; border-radius: 8px; border: 1px solid #ffe0b2;">
                <h3 style="margin: 0; color: #f57c00; font-size: 24px;">{active_announcements}</h3>
                <p style="margin: 5px 0 0 0; color: #555; font-size: 14px;">الإعلانات النشطة</p>
            </div>
        </div>

        <!-- أزرار الإدارة والتحكم -->
        <h4 style="color: #444; border-bottom: 1px solid #ddd; padding-bottom: 5px;">🎛️ أقسام الإدارة والتحكم</h4>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 15px;">
            <a href="/admin/staff-manage" class="btn" style="text-align: center; padding: 15px; font-size: 16px; background: #1976d2;">👨‍⚕️ إدارة العناصر الطبية</a>
            <a href="/admin/donors-manage" class="btn" style="text-align: center; padding: 15px; font-size: 16px; background: #388e3c;">👥 إدارة ومتابعة المتبرعين</a>
            <a href="/admin/statistics" class="btn" style="text-align: center; padding: 15px; font-size: 16px; background: #f57c00;">📊 الإحصائيات والتقارير الشاملة</a>
            <a href="/admin/announcements" class="btn" style="text-align: center; padding: 15px; font-size: 16px; background: #9a0007;">📢 إدارة الإعلانات ونداءات الدم</a>
        </div>
    </div>
    '''
    return render_main_page(body)

@admin_bp.route('/staff-manage', methods=['GET', 'POST'])
def staff_manage():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        staff_code = request.form.get('staff_code')
        full_name = request.form.get('full_name')
        specialty = request.form.get('specialty')
        workplace = request.form.get('workplace')
        phone = request.form.get('phone')
        whatsapp = request.form.get('whatsapp')
        password = request.form.get('password')
        
        try:
            cursor.execute("""
                INSERT INTO medical_staff (staff_code, full_name, specialty, workplace, phone, whatsapp, role, password)
                VALUES (?, ?, ?, ?, ?, ?, 'staff', ?)
            """, (staff_code, full_name, specialty, workplace, phone, whatsapp, password))
            conn.commit()
            flash('تمت إضافة العنصر الطبي بنجاح!', 'success')
        except Exception as e:
            flash('خطأ: كود الموظف مستخدم مسبقاً أو بيانات غير صالحة.', 'error')
            
        conn.close()
        return redirect(url_for('admin.staff_manage'))
        
    cursor.execute("SELECT * FROM medical_staff ORDER BY id DESC")
    staff_list = cursor.fetchall()
    conn.close()

    staff_rows = ""
    for s in staff_list:
        staff_rows += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{s['staff_code']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{s['full_name']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{s['specialty']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{s['phone']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: center;">
                {f"<a href='/admin/staff-delete/{s['id']}' style='color: #d32f2f; text-decoration: none;'>حذف</a>" if s['role'] != 'admin' else "مسؤول النظام"}
            </td>
        </tr>
        """

    body = f'''
    <div class="card" style="max-width: 900px; margin: 0 auto;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #d32f2f; padding-bottom: 12px; margin-bottom: 20px;">
            <h2 style="color: #9a0007; margin: 0;">👨‍⚕️ إدارة العناصر الطبية</h2>
            <a href="/admin/dashboard" class="btn btn-secondary" style="padding: 6px 15px; font-size: 14px;">العودة للوحة التحكم</a>
        </div>

        <!-- نموذج إضافة موظف جديد -->
        <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 25px;">
            <h4 style="margin-top: 0; color: #333;">➕ إضافة عنصر طبي جديد</h4>
            <form method="POST">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
                    <input type="text" name="staff_code" required placeholder="كود الموظف (مثال: MED-102)" style="padding: 10px; border: 1px solid #ccc; border-radius: 6px;">
                    <input type="text" name="full_name" required placeholder="الاسم الكامل" style="padding: 10px; border: 1px solid #ccc; border-radius: 6px;">
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
                    <input type="text" name="specialty" placeholder="التخصص (مثال: تحاليل مخبرية)" style="padding: 10px; border: 1px solid #ccc; border-radius: 6px;">
                    <input type="text" name="workplace" placeholder="مقر العمل" style="padding: 10px; border: 1px solid #ccc; border-radius: 6px;">
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-bottom: 15px;">
                    <input type="text" name="phone" required placeholder="رقم الهاتف" style="padding: 10px; border: 1px solid #ccc; border-radius: 6px;">
                    <input type="text" name="whatsapp" placeholder="رقم الواتساب" style="padding: 10px; border: 1px solid #ccc; border-radius: 6px;">
                    <input type="password" name="password" required placeholder="الرقم السري" style="padding: 10px; border: 1px solid #ccc; border-radius: 6px;">
                </div>
                <button type="submit" class="btn" style="padding: 10px 20px;">حفظ وإضافة الموظف</button>
            </form>
        </div>

        <!-- جدول العناصر الطبية -->
        <h4 style="color: #444;">📋 قائمة العناصر الطبية المسجلة</h4>
        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; text-align: right; font-size: 14px;">
                <thead>
                    <tr style="background: #f1f1f1;">
                        <th style="padding: 10px; border-bottom: 2px solid #ccc;">الكود</th>
                        <th style="padding: 10px; border-bottom: 2px solid #ccc;">الاسم</th>
                        <th style="padding: 10px; border-bottom: 2px solid #ccc;">التخصص</th>
                        <th style="padding: 10px; border-bottom: 2px solid #ccc;">الهاتف</th>
                        <th style="padding: 10px; border-bottom: 2px solid #ccc; text-align: center;">الإجراء</th>
                    </tr>
                </thead>
                <tbody>
                    {staff_rows}
                </tbody>
            </table>
        </div>
    </div>
    '''
    return render_main_page(body)

@admin_bp.route('/staff-delete/<int:staff_id>')
def staff_delete(staff_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medical_staff WHERE id = ? AND role != 'admin'", (staff_id,))
    conn.commit()
    conn.close()
    flash('تم حذف العنصر الطبي بنجاح.', 'success')
    return redirect(url_for('admin.staff_manage'))

@admin_bp.route('/donors-manage')
def donors_manage():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM donors ORDER BY id DESC")
    donors = cursor.fetchall()
    conn.close()

    donors_rows = ""
    for d in donors:
        verified_text = f"✔ (بواسطة: {d['verified_by_staff'] or 'طبيب'})" if d['blood_type_verified'] else "⏳ غير مؤكد"
        donors_rows += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{d['donor_number']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{d['full_name']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{d['phone']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd; font-weight: bold; color: #9a0007;">{d['blood_type'] or '--'}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd; font-size: 12px;">{verified_text}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: center;">
                <a href="/admin/donor-delete/{d['id']}" style="color: #d32f2f; text-decoration: none; font-size: 13px;">حذف</a>
            </td>
        </tr>
        """

    body = f'''
    <div class="card" style="max-width: 950px; margin: 0 auto;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #d32f2f; padding-bottom: 12px; margin-bottom: 20px;">
            <h2 style="color: #9a0007; margin: 0;">👥 إدارة ومتابعة المتبرعين</h2>
            <a href="/admin/dashboard" class="btn btn-secondary" style="padding: 6px 15px; font-size: 14px;">العودة للوحة التحكم</a>
        </div>

        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; text-align: right; font-size: 14px;">
                <thead>
                    <tr style="background: #f1f1f1;">
                        <th style="padding: 10px; border-bottom: 2px solid #ccc;">رقم المتبرع</th>
                        <th style="padding: 10px; border-bottom: 2px solid #ccc;">الاسم الثلاثي</th>
                        <th style="padding: 10px; border-bottom: 2px solid #ccc;">الهاتف</th>
                        <th style="padding: 10px; border-bottom: 2px solid #ccc;">الفصيلة</th>
                        <th style="padding: 10px; border-bottom: 2px solid #ccc;">حالة التوثيق والمسؤول</th>
                        <th style="padding: 10px; border-bottom: 2px solid #ccc; text-align: center;">الإجراء</th>
                    </tr>
                </thead>
                <tbody>
                    {donors_rows if donors_rows else '<tr><td colspan="6" style="text-align: center; padding: 15px; color: #666;">لا يوجد متبرعون مسجلون حالياً.</td></tr>'}
                </tbody>
            </table>
        </div>
    </div>
    '''
    return render_main_page(body)

@admin_bp.route('/donor-delete/<int:donor_id>')
def donor_delete(donor_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM donors WHERE id = ?", (donor_id,))
    conn.commit()
    conn.close()
    flash('تم حذف ملف المتبرع بنجاح.', 'success')
    return redirect(url_for('admin.donors_manage'))

@admin_bp.route('/statistics')
def statistics():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM donors")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM donors WHERE virus_status != 'سليم'")
    viral_cases = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM donors WHERE donation_completed = 0")
    incomplete_donations = cursor.fetchone()[0]
    
    # الإحصائيات حسب الفصيلة
    blood_counts = {}
    for b in ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']:
        cursor.execute("SELECT COUNT(*) FROM donors WHERE blood_type = ?", (b,))
        blood_counts[b] = cursor.fetchone()[0]
        
    conn.close()

    blood_stats_html = ""
    for b, count in blood_counts.items():
        blood_stats_html += f"""
        <div style="background: #f9f9f9; padding: 12px; border-radius: 6px; text-align: center; border: 1px solid #ddd;">
            <strong style="font-size: 18px; color: #9a0007;">{b}</strong><br>
            <span style="font-size: 20px; font-weight: bold; color: #333;">{count}</span> متبرع
        </div>
        """

    body = f'''
    <div class="card" style="max-width: 900px; margin: 0 auto;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #d32f2f; padding-bottom: 12px; margin-bottom: 20px;">
            <h2 style="color: #9a0007; margin: 0;">📊 الإحصائيات والتقارير الشاملة</h2>
            <a href="/admin/dashboard" class="btn btn-secondary" style="padding: 6px 15px; font-size: 14px;">العودة للوحة التحكم</a>
        </div>

        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px; text-align: center;">
            <div style="background: #e3f2fd; padding: 15px; border-radius: 8px;">
                <h3 style="margin: 0; color: #1565c0; font-size: 22px;">{total}</h3>
                <p style="margin: 5px 0 0 0; color: #555; font-size: 13px;">إجمالي المتبرعين</p>
            </div>
            <div style="background: #ffebee; padding: 15px; border-radius: 8px;">
                <h3 style="margin: 0; color: #d32f2f; font-size: 22px;">{viral_cases}</h3>
                <p style="margin: 5px 0 0 0; color: #555; font-size: 13px;">حالات تحتاج مراجعة/فيروسات</p>
            </div>
            <div style="background: #fff8e1; padding: 15px; border-radius: 8px;">
                <h3 style="margin: 0; color: #f57c00; font-size: 22px;">{incomplete_donations}</h3>
                <p style="margin: 5px 0 0 0; color: #555; font-size: 13px;">تبرعات لم تكتمل</p>
            </div>
        </div>

        <h4 style="color: #444; border-bottom: 1px solid #ddd; padding-bottom: 5px;">🩸 توزيع المتبرعين حسب فصائل الدم</h4>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 25px;">
            {blood_stats_html}
        </div>

        <div style="text-align: center; margin-top: 20px;">
            <button onclick="window.print();" class="btn" style="padding: 10px 25px;">🖨️ طباعة تقرير الإحصائيات (A4)</button>
        </div>
    </div>
    '''
    return render_main_page(body)

@admin_bp.route('/announcements', methods=['GET', 'POST'])
def announcements():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        blood_type_needed = request.form.get('blood_type_needed')
        urgency_level = request.form.get('urgency_level')
        units_required = request.form.get('units_required') or 0
        
        cursor.execute("""
            INSERT INTO announcements (title, content, blood_type_needed, urgency_level, units_required)
            VALUES (?, ?, ?, ?, ?)
        """, (title, content, blood_type_needed, urgency_level, units_required))
        conn.commit()
        flash('تم نشر الإعلان أو النداء بنجاح في الشاشة الرئيسية!', 'success')
        conn.close()
        return redirect(url_for('admin.announcements'))
        
    cursor.execute("SELECT * FROM announcements ORDER BY id DESC")
    announcements_list = cursor.fetchall()
    conn.close()

    ann_rows = ""
    for a in announcements_list:
        badge_bg = "#ffebee" if a['urgency_level'] == 'عاجل' else "#fff8e1"
        ann_rows += f"""
        <div style="background: {badge_bg}; padding: 12px; border-radius: 6px; margin-bottom: 10px; border: 1px solid #ddd; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h4 style="margin: 0 0 5px 0; color: #9a0007;">{a['title']} {f"(فصيلة: {a['blood_type_needed']})" if a['blood_type_needed'] else ""} - [{a['urgency_level']}]</h4>
                <p style="margin: 0; font-size: 14px;">{a['content']}</p>
                {f"<small style='color: #d32f2f; font-weight: bold;'>الوحدات المطلوبة: {a['units_required']}</small>" if a['units_required'] else ""}
            </div>
            <div>
                <a href="/admin/announcement-delete/{a['id']}" style="color: #d32f2f; text-decoration: none; font-size: 13px; font-weight: bold;">حذف</a>
            </div>
        </div>
        """

    body = f'''
    <div class="card" style="max-width: 900px; margin: 0 auto;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #d32f2f; padding-bottom: 12px; margin-bottom: 20px;">
            <h2 style="color: #9a0007; margin: 0;">📢 إدارة الإعلانات ونداءات التبرع</h2>
            <a href="/admin/dashboard" class="btn btn-secondary" style="padding: 6px 15px; font-size: 14px;">العودة للوحة التحكم</a>
        </div>

        <!-- نموذج إنشاء إعلان جديد -->
        <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 25px;">
            <h4 style="margin-top: 0; color: #333;">➕ تجهيز إعلان أو نداء تبرع جديد</h4>
            <form method="POST">
                <div style="margin-bottom: 10px;">
                    <input type="text" name="title" required placeholder="عنوان الإعلان أو النداء (مثال: نداء عاجل لتوفير دم لطفل)" style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box;">
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-bottom: 10px;">
                    <select name="blood_type_needed" style="padding: 10px; border: 1px solid #ccc; border-radius: 6px;">
                        <option value="">كل الفصائل / عام</option>
                        <option value="A+">A+</option><option value="A-">A-</option>
                        <option value="B+">B+</option><option value="B-">B-</option>
                        <option value="O+">O+</option><option value="O-">O-</option>
                        <option value="AB+">AB+</option><option value="AB-">AB-</option>
                    </select>
                    <select name="urgency_level" style="padding: 10px; border: 1px solid #ccc; border-radius: 6px;">
                        <option value="عادي">إعلان عادي / حملة</option>
                        <option value="عاجل">طارئ وعاجل جداً</option>
                    </select>
                    <input type="number" name="units_required" placeholder="عدد الوحدات المطلوبة" style="padding: 10px; border: 1px solid #ccc; border-radius: 6px;">
                </div>
                <div style="margin-bottom: 15px;">
                    <textarea name="content" rows="3" required placeholder="نص النداء أو التفاصيل (مثال: الرجاء التوجه إلى مصرف الدم المركزي - صبراتة للحالة الطارئة...)" style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box;"></textarea>
                </div>
                <button type="submit" class="btn" style="padding: 10px 25px;">نشر الإعلان على الشاشة الرئيسية</button>
            </form>
        </div>

        <!-- قائمة الإعلانات الحالية -->
        <h4 style="color: #444;">📌 الإعلانات والنداءات النشطة حالياً</h4>
        <div>
            {ann_rows if ann_rows else '<p style="color: #666; text-align: center; padding: 10px;">لا توجد إعلانات منشورة حالياً.</p>'}
        </div>
    </div>
    '''
    return render_main_page(body)

@admin_bp.route('/announcement-delete/<int:ann_id>')
def announcement_delete(ann_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM announcements WHERE id = ?", (ann_id,))
    conn.commit()
    conn.close()
    flash('تم حذف الإعلان بنجاح.', 'success')
    return redirect(url_for('admin.announcements'))
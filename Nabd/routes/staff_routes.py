from flask import Blueprint, render_template_string, request, session, redirect, url_for, flash
from database import get_db_connection
from templates_helper import render_main_page

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')

@staff_bp.route('/dashboard')
def dashboard():
    # التأكد من أن المستخدم كادر طبي أو مسؤول
    if 'user_id' not in session or session.get('role') not in ['staff', 'admin']:
        return redirect(url_for('auth.login'))
        
    staff_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # جلب بيانات الطبيب
    cursor.execute("SELECT * FROM medical_staff WHERE id = ?", (staff_id,))
    staff = cursor.fetchone()
    
    # استقبال نص البحث إن وجد
    search_query = request.args.get('q', '')
    donors = []
    if search_query:
        cursor.execute("""
            SELECT * FROM donors 
            WHERE full_name LIKE ? OR phone LIKE ? OR donor_number LIKE ?
            ORDER BY id DESC
        """, (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
        donors = cursor.fetchall()
    else:
        cursor.execute("SELECT * FROM donors ORDER BY id DESC LIMIT 10")
        donors = cursor.fetchall()
        
    conn.close()

    donors_rows = ""
    for d in donors:
        verified_icon = "✔" if d['blood_type_verified'] else "⏳"
        donors_rows += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{d['donor_number']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{d['full_name']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{d['phone']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd; font-weight: bold; color: #9a0007;">{d['blood_type'] or '--'} {verified_icon}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: center;">
                <a href="/staff/donor/{d['id']}" class="btn" style="padding: 5px 10px; font-size: 13px;">فتح الملف والتحرير</a>
            </td>
        </tr>
        """

    body = f'''
    <div class="card" style="max-width: 900px; margin: 0 auto;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #d32f2f; padding-bottom: 12px; margin-bottom: 20px;">
            <h2 style="color: #9a0007; margin: 0;">🩺 لوحة تحكم الكادر الطبي</h2>
            <a href="/logout" class="btn" style="background: #d32f2f; padding: 6px 15px; font-size: 14px;">تسجيل الخروج</a>
        </div>

        <!-- بيانات العنصر الطبي -->
        <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="margin: 0 0 5px 0; color: #333;">د. {staff['full_name']}</h3>
                <p style="margin: 3px 0; color: #666; font-size: 14px;">التخصص/الصفة: <strong>{staff['specialty']}</strong> | الكود: <strong>{staff['staff_code']}</strong></p>
                <p style="margin: 3px 0; color: #666; font-size: 14px;">مقر العمل: {staff['workplace']}</p>
            </div>
            <div>
                <span style="background: #e3f2fd; color: #1976d2; padding: 6px 12px; border-radius: 6px; font-size: 13px; font-weight: bold;">كادر معتمد</span>
            </div>
        </div>

        <!-- قسم البحث السريع وقراءة الباركود -->
        <div class="card" style="background: #fff8e1; margin-bottom: 20px;">
            <h4 style="margin-top: 0; color: #f57c00;">🔍 البحث السريع عن المتبرع أو مسح الباركود</h4>
            <form method="GET" action="/staff/dashboard" style="display: flex; gap: 10px;">
                <input type="text" name="q" value="{search_query}" placeholder="ابحث بالاسم، رقم الهاتف، أو رقم المتبرع (مثل D-001)..." style="flex-grow: 1; padding: 10px; border: 1px solid #ccc; border-radius: 6px;">
                <button type="submit" class="btn" style="padding: 10px 20px;">بحث</button>
            </form>
        </div>

        <!-- جدول المتبرعين -->
        <h4 style="color: #444;">📋 قائمة المتبرعين (آخر التسجيلات)</h4>
        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; text-align: right; font-size: 14px;">
                <thead>
                    <tr style="background: #f1f1f1;">
                        <th style="padding: 10px; border-bottom: 2px solid #ccc;">رقم المتبرع</th>
                        <th style="padding: 10px; border-bottom: 2px solid #ccc;">الإسم الثلاثي</th>
                        <th style="padding: 10px; border-bottom: 2px solid #ccc;">رقم الهاتف</th>
                        <th style="padding: 10px; border-bottom: 2px solid #ccc;">فصيلة الدم</th>
                        <th style="padding: 10px; border-bottom: 2px solid #ccc; text-align: center;">الإجراء</th>
                    </tr>
                </thead>
                <tbody>
                    {donors_rows if donors_rows else '<tr><td colspan="5" style="text-align: center; padding: 15px; color: #666;">لا توجد نتائج مطابقة للبحث.</td></tr>'}
                </tbody>
            </table>
        </div>
    </div>
    '''
    return render_main_page(body)

@staff_bp.route('/donor/<int:donor_id>', methods=['GET', 'POST'])
def edit_donor_medical(donor_id):
    if 'user_id' not in session or session.get('role') not in ['staff', 'admin']:
        return redirect(url_for('auth.login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        weight = request.form.get('weight')
        height = request.form.get('height')
        blood_pressure = request.form.get('blood_pressure')
        blood_type = request.form.get('blood_type')
        blood_type_verified = 1 if request.form.get('blood_type_verified') else 0
        virus_status = request.form.get('virus_status')
        lab_results = request.form.get('lab_results')
        donation_completed = 1 if request.form.get('donation_completed') else 0
        
        staff_name = session.get('user_name')
        
        cursor.execute("""
            UPDATE donors SET 
                weight = ?, height = ?, blood_pressure = ?, blood_type = ?, 
                blood_type_verified = ?, verified_by_staff = ?, virus_status = ?, 
                lab_results = ?, donation_completed = ?
            WHERE id = ?
        """, (weight, height, blood_pressure, blood_type, blood_type_verified, staff_name, virus_status, lab_results, donation_completed, donor_id))
        
        # تسجيل العملية في السجلات الطبية
        cursor.execute("""
            INSERT INTO medical_logs (staff_id, donor_id, action_details)
            VALUES (?, ?, ?)
        """, (session['user_id'], donor_id, f"تم تحديث البيانات الطبية وتأكيد الفصيلة بواسطة {staff_name}"))
        
        conn.commit()
        conn.close()
        flash('تم تحديث البيانات الطبية للمتبرع بنجاح!', 'success')
        return redirect(url_for('staff.dashboard'))
        
    cursor.execute("SELECT * FROM donors WHERE id = ?", (donor_id,))
    donor = cursor.fetchone()
    conn.close()
    
    if not donor:
        return redirect(url_for('staff.dashboard'))

    is_verified_checked = "checked" if donor['blood_type_verified'] else ""
    is_completed_checked = "checked" if donor['donation_completed'] else ""

    body = f'''
    <div class="card" style="max-width: 700px; margin: 0 auto;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #d32f2f; padding-bottom: 12px; margin-bottom: 20px;">
            <h2 style="color: #9a0007; margin: 0;">🩺 تحرير ملف المتبرع الطبي</h2>
            <a href="/staff/dashboard" class="btn btn-secondary" style="padding: 6px 15px; font-size: 14px;">العودة للوحة التحكم</a>
        </div>

        <div style="background: #f9f9f9; padding: 12px; border-radius: 6px; margin-bottom: 20px;">
            <h3 style="margin: 0 0 5px 0;">{donor['full_name']}</h3>
            <p style="margin: 0; font-size: 14px; color: #666;">رقم المتبرع: <strong>{donor['donor_number']}</strong> | الهاتف: {donor['phone']}</p>
        </div>

        <form method="POST">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                <div>
                    <label style="display: block; margin-bottom: 5px; font-weight: bold;">الوزن (كغ):</label>
                    <input type="text" name="weight" value="{donor['weight'] or ''}" placeholder="مثال: 75" style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box;">
                </div>
                <div>
                    <label style="display: block; margin-bottom: 5px; font-weight: bold;">الطول (سم):</label>
                    <input type="text" name="height" value="{donor['height'] or ''}" placeholder="مثال: 175" style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box;">
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                <div>
                    <label style="display: block; margin-bottom: 5px; font-weight: bold;">ضغط الدم:</label>
                    <input type="text" name="blood_pressure" value="{donor['blood_pressure'] or ''}" placeholder="مثال: 120/80" style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box;">
                </div>
                <div>
                    <label style="display: block; margin-bottom: 5px; font-weight: bold;">فصيلة الدم:</label>
                    <select name="blood_type" style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box;">
                        <option value="">اختر الفصيلة</option>
                        <option value="A+" {"selected" if donor['blood_type'] == 'A+' else ""}>A+</option>
                        <option value="A-" {"selected" if donor['blood_type'] == 'A-' else ""}>A-</option>
                        <option value="B+" {"selected" if donor['blood_type'] == 'B+' else ""}>B+</option>
                        <option value="B-" {"selected" if donor['blood_type'] == 'B-' else ""}>B-</option>
                        <option value="O+" {"selected" if donor['blood_type'] == 'O+' else ""}>O+</option>
                        <option value="O-" {"selected" if donor['blood_type'] == 'O-' else ""}>O-</option>
                        <option value="AB+" {"selected" if donor['blood_type'] == 'AB+' else ""}>AB+</option>
                        <option value="AB-" {"selected" if donor['blood_type'] == 'AB-' else ""}>AB-</option>
                    </select>
                </div>
            </div>

            <div style="margin-bottom: 15px; background: #fff8e1; padding: 10px; border-radius: 6px;">
                <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; font-weight: bold; color: #f57c00;">
                    <input type="checkbox" name="blood_type_verified" value="1" {is_verified_checked} style="width: 18px; height: 18px;">
                    تأكيد صحة فصيلة الدم رسمياً بعلامة التوثيق
                </label>
                {f"<p style='margin: 5px 0 0 26px; font-size: 12px; color: #666;'>آخر تأكيد بواسطة: {donor['verified_by_staff']}</p>" if donor['verified_by_staff'] else ""}
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                <div>
                    <label style="display: block; margin-bottom: 5px; font-weight: bold;">حالة الفيروسات:</label>
                    <select name="virus_status" style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box;">
                        <option value="سليم" {"selected" if donor['virus_status'] == 'سليم' else ""}>سليم (آمن)</option>
                        <option value="يحتاج مراجعة" {"selected" if donor['virus_status'] == 'يحتاج مراجعة' else ""}>يحتاج مراجعة</option>
                        <option value="إيجابي" {"selected" if donor['virus_status'] == 'إيجابي' else ""}>إيجابي (مخالف)</option>
                    </select>
                </div>
                <div style="display: flex; align-items: center; padding-top: 25px;">
                    <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; font-weight: bold; color: #388e3c;">
                        <input type="checkbox" name="donation_completed" value="1" {is_completed_checked} style="width: 18px; height: 18px;">
                        اكتمل التبرع بنجاح اليوم
                    </label>
                </div>
            </div>

            <div style="margin-bottom: 20px;">
                <label style="display: block; margin-bottom: 5px; font-weight: bold;">الملاحظات الطبية والتحاليل:</label>
                <textarea name="lab_results" rows="3" placeholder="أدخل أي ملاحظات إضافية..." style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box;">{donor['lab_results'] or ''}</textarea>
            </div>

            <button type="submit" class="btn" style="width: 100%; padding: 12px; font-size: 16px;">حفظ وتحديث الملف الطبي</button>
        </form>
    </div>
    '''
    return render_main_page(body)
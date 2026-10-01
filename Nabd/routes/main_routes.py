from flask import Blueprint, render_template_string
from database import get_db_connection
from templates_helper import render_main_page

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # جلب الإعلانات النشطة من قاعدة البيانات
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM announcements WHERE is_active = 1 ORDER BY id DESC")
    announcements = cursor.fetchall()
    conn.close()
    
    # بناء قسم لوحة الإعلانات
    announcements_html = ""
    if announcements:
        for ann in announcements:
            urgency_style = "border-right: 5px solid #d32f2f; background: #ffebee;" if ann['urgency_level'] == 'عاجل' else "border-right: 5px solid #ff9800; background: #fff8e1;"
            announcements_html += f"""
            <div style="padding: 12px; margin-bottom: 10px; border-radius: 6px; {urgency_style}">
                <h4 style="margin: 0 0 5px 0; color: #9a0007;">📢 {ann['title']} {f"(فصيلة مطلوبة: {ann['blood_type_needed']})" if ann['blood_type_needed'] else ""}</h4>
                <p style="margin: 0; font-size: 14px;">{ann['content']}</p>
                {f"<p style='margin: 5px 0 0 0; font-size: 12px; font-weight: bold; color: #d32f2f;'>الunits المطلوبة: {ann['units_required']} وحدة</p>" if ann['units_required'] else ""}
            </div>
            """
    else:
        announcements_html = "<p style='text-align: center; color: #666;'>لا توجد إعلانات أو نداءات تبرع نشطة حالياً.</p>"

    body = f'''
    <div class="card" style="text-align: center;">
        <h2 style="color: #9a0007; font-size: 26px;">نبض الحياة.. قطرة منك تصنع فرقاً ❤️</h2>
        <p style="font-size: 16px; line-height: 1.6; color: #555;">
            المنصة الذكية الرسمية لمصرف الدم المركزي - صبراتة. نربط المتبرعين، الكادر الطبي، وإدارة المصرف بروح إنسانية عالية وبتقنية رقمية متكاملة.
        </p>
        
        <div style="margin: 25px 0;">
            <a href="/login" class="btn" style="font-size: 18px; padding: 12px 30px;">تسجيل الدخول للنظام</a>
            <a href="/donor/register" class="btn btn-secondary" style="font-size: 18px; padding: 12px 30px;">إنشاء حساب متبرع جديد</a>
        </div>
    </div>

    <!-- لوحة الإعلانات الإدارية -->
    <div class="card">
        <h3 style="border-bottom: 2px solid #d32f2f; padding-bottom: 8px; margin-top: 0;">📌 لوحة إعلانات ونداءات مصرف الدم</h3>
        <div style="margin-top: 15px;">
            {announcements_html}
        </div>
    </div>

    <!-- حالة التبرع ومشتقات الدم -->
    <div class="card">
        <h3 style="margin-top: 0;">🩸 حالة توفر مشتقات الدم في المصرف</h3>
        <p style="font-size: 14px; color: #666;">نظرة عامة على حالة التبرع النشطة والوحدات المتاحة للمساهمة المجتمعية:</p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 10px; text-align: center; margin-top: 15px;">
            <div style="background: #f1f8e9; padding: 10px; border-radius: 8px; border: 1px solid #c8e6c9;"><strong>A+</strong><br><span style="color: #388e3c; font-size: 14px;">متوفر</span></div>
            <div style="background: #ffebee; padding: 10px; border-radius: 8px; border: 1px solid #ffcdd2;"><strong>A-</strong><br><span style="color: #d32f2f; font-size: 14px;">منخفض</span></div>
            <div style="background: #f1f8e9; padding: 10px; border-radius: 8px; border: 1px solid #c8e6c9;"><strong>B+</strong><br><span style="color: #388e3c; font-size: 14px;">متوفر</span></div>
            <div style="background: #fff8e1; padding: 10px; border-radius: 8px; border: 1px solid #ffe0b2;"><strong>O+</strong><br><span style="color: #f57c00; font-size: 14px;">مستقر</span></div>
            <div style="background: #ffebee; padding: 10px; border-radius: 8px; border: 1px solid #ffcdd2;"><strong>O-</strong><br><span style="color: #d32f2f; font-size: 14px;">حرج جداً</span></div>
            <div style="background: #f1f8e9; padding: 10px; border-radius: 8px; border: 1px solid #c8e6c9;"><strong>AB+</strong><br><span style="color: #388e3c; font-size: 14px;">متوفر</span></div>
        </div>
    </div>
    '''
    return render_main_page(body)
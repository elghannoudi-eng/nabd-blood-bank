from flask import render_template_string

def render_main_page(body_content):
    base_html = '''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>تطبيق نَبض - Nabd System</title>
        <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary-red: #d32f2f;
                --dark-red: #9a0007;
                --light-bg: #f8f9fa;
                --card-bg: #ffffff;
                --text-color: #333333;
                --gray-border: #e0e0e0;
            }
            body {
                font-family: 'Cairo', sans-serif;
                background-color: var(--light-bg);
                color: var(--text-color);
                margin: 0;
                padding: 0;
            }
            header {
                background: linear-gradient(135deg, var(--dark-red), var(--primary-red));
                color: white;
                padding: 20px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .container {
                max-width: 900px;
                margin: 20px auto;
                padding: 20px;
            }
            .card {
                background: var(--card-bg);
                border-radius: 12px;
                padding: 25px;
                margin-bottom: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                border-top: 4px solid var(--primary-red);
            }
            h1, h2, h3 { color: var(--dark-red); }
            .btn {
                background-color: var(--primary-red);
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-family: 'Cairo', sans-serif;
                font-size: 16px;
                text-decoration: none;
                display: inline-block;
                transition: background 0.3s;
                margin: 5px;
            }
            .btn:hover { background-color: var(--dark-red); }
            .btn-secondary { background-color: #555; }
            .btn-secondary:hover { background-color: #333; }
            input, select, textarea {
                width: 100%;
                padding: 10px;
                margin: 8px 0 15px 0;
                border: 1px solid var(--gray-border);
                border-radius: 6px;
                box-sizing: border-box;
                font-family: 'Cairo', sans-serif;
            }
            .qr-box {
                text-align: center;
                background: #fff;
                padding: 15px;
                border-radius: 8px;
                display: inline-block;
                border: 1px solid var(--gray-border);
            }
            .badge {
                background: #ffebee;
                color: var(--primary-red);
                padding: 5px 10px;
                border-radius: 20px;
                font-weight: bold;
                display: inline-block;
            }
            .flex-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>نَبض | NABD SYSTEM</h1>
            <p>المنصة الذكية لإدارة الدم والمتبرعين - مصرف الدم المركزي صبراتة</p>
        </header>
        <div class="container">
            ''' + body_content + '''
        </div>
    </body>
    </html>
    '''
    return render_template_string(base_html)
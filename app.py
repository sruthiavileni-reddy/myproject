from flask import Flask, render_template, jsonify, send_file, request
from flask_cors import CORS
import sqlite3
import qrcode
from io import BytesIO
import base64
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Initialize Database
def init_db():
    conn = sqlite3.connect('certificates.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS certificates
                 (id TEXT PRIMARY KEY, 
                  name TEXT, 
                  domain TEXT, 
                  issue_date TEXT,
                  certificate_url TEXT)''')
    
    # Sample 10 certificates
    certificates = [
        ('CERT001', 'DEVARAKONDA ANIRUDH', 'FULL STACK WEB DEVELOPMENT', '2025-09-01', 'https://i.postimg.cc/Y9MD2Mty/ANIRUDH.jpg'),
        ('CERT002', 'PANTULA VENKATA GANA SIVA SAI', 'CYBER SECURITY', '2025-09-01', 'https://i.postimg.cc/example1.jpg'),
        ('CERT003', 'RAJESH KUMAR', 'DATA SCIENCE', '2025-08-15', 'https://i.postimg.cc/example2.jpg'),
        ('CERT004', 'PRIYA SHARMA', 'ARTIFICIAL INTELLIGENCE', '2025-07-20', 'https://i.postimg.cc/example3.jpg'),
        ('CERT005', 'AMIT PATEL', 'CLOUD COMPUTING', '2025-08-01', 'https://i.postimg.cc/example4.jpg'),
        ('CERT006', 'SNEHA REDDY', 'MOBILE APP DEVELOPMENT', '2025-09-10', 'https://i.postimg.cc/example5.jpg'),
        ('CERT007', 'VIKRAM SINGH', 'BLOCKCHAIN TECHNOLOGY', '2025-07-05', 'https://i.postimg.cc/example6.jpg'),
        ('CERT008', 'ANANYA IYER', 'MACHINE LEARNING', '2025-08-25', 'https://i.postimg.cc/example7.jpg'),
        ('CERT009', 'KARTHIK RAO', 'DEVOPS ENGINEERING', '2025-09-15', 'https://i.postimg.cc/example8.jpg'),
        ('CERT010', 'MEERA NAIR', 'UI/UX DESIGN', '2025-08-10', 'https://i.postimg.cc/example9.jpg')
    ]
    
    c.executemany('INSERT OR IGNORE INTO certificates VALUES (?,?,?,?,?)', certificates)
    conn.commit()
    conn.close()

# Generate QR Code
def generate_qr(cert_id):
    # QR code now points to the verification page
    verification_url = f"http://.192.168.29.167:5000/verify/{cert_id}"
    qr=qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(verification_url)
    qr.make(fit=True)
    img=qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

# API Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/verify/<cert_id>')
def verify_certificate(cert_id):
    # This shows the simple verification page with green checkmark
    return render_template('verify.html', cert_id=cert_id)

@app.route('/certificate/<cert_id>')
def full_certificate(cert_id):
    # This shows the full certificate page
    return render_template('certificate.html', cert_id=cert_id)

@app.route('/api/certificate/<cert_id>')
def get_certificate(cert_id):
    conn = sqlite3.connect('certificates.db')
    c = conn.cursor()
    c.execute('SELECT * FROM certificates WHERE id=?', (cert_id,))
    result = c.fetchone()
    conn.close()
    
    if result:
        qr_code = generate_qr(cert_id)
        return jsonify({
            'success': True,
            'id': result[0],
            'name': result[1],
            'domain': result[2],
            'issue_date': result[3],
            'certificate_url': result[4],
            'qr_code': qr_code
        })
    else:
        return jsonify({'success': False, 'message': 'Certificate not found'})

@app.route('/api/certificates')
def get_all_certificates():
    conn = sqlite3.connect('certificates.db')
    c = conn.cursor()
    c.execute('SELECT id, name, domain FROM certificates')
    results = c.fetchall()
    conn.close()
    
    certificates = [{'id': r[0], 'name': r[1], 'domain': r[2]} for r in results]
    return jsonify(certificates)

@app.route('/api/search')
def search_certificate():
    name = request.args.get('name', '').upper()
    
    conn = sqlite3.connect('certificates.db')
    c = conn.cursor()
    # Search for exact match or partial match
    c.execute('SELECT id, name FROM certificates WHERE UPPER(name) LIKE ?', (f'%{name}%',))
    result = c.fetchone()
    conn.close()
    
    if result:
        return jsonify({
            'success': True,
            'id': result[0],
            'name': result[1]
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Certificate not found'
        })

if __name__ == '__main__':
    import webbrowser
    from threading import Timer
    
    PORT = 5000
    
    init_db()
    print("🚀 Server starting at http://localhost:{PORT}")
    print("📋 Database initialized with 10 sample certificates")
    print("🌐 Opening browser automatically in 2 seconds...")
    
    # Open browser automatically after 2 seconds
    def open_browser():
        webbrowser.open(f'http://localhost:{PORT}')
    
    Timer(2, open_browser).start()
    
    app.run(debug=True,host='0.0.0.0', port=PORT, use_reloader=False)
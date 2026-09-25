from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json
import os
import time
import random
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import uuid
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max
app.config['DATABASE'] = 'database/wajahku.db'
app.config['JWT_SECRET_KEY'] = 'wajahku-secret-key-2024-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Enable CORS for React frontend
CORS(app, resources={r"/api/*": {"origins": "*", "allow_headers": ["Content-Type", "Authorization"]}})

jwt = JWTManager(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Skin conditions database
SKIN_CONDITIONS = {
    'jerawat': {
        'name': 'Jerawat (Acne)',
        'description': 'Terdapat peradangan dan komedo pada kulit wajah. Bisa disebabkan oleh produksi minyak berlebih, bakteri, atau hormon.'
    },
    'berminyak': {
        'name': 'Kulit Berminyak',
        'description': 'Produksi sebum berlebihan yang membuat wajah terlihat mengkilap dan pori-pori membesar.'
    },
    'kering': {
        'name': 'Kulit Kering',
        'description': 'Kulit terasa kencang, kasar, dan kusam karena kurangnya kelembaban alami.'
    },
    'kusam': {
        'name': 'Kulit Kusam',
        'description': 'Warna kulit tidak merata dan terlihat tidak bercahaya, biasanya karena sel kulit mati menumpuk.'
    },
    'kemerahan': {
        'name': 'Kemerahan (Redness)',
        'description': 'Area kulit yang memerah, bisa karena iritasi, sensitivitas, atau peradangan.'
    },
    'kombinasi': {
        'name': 'Kulit Kombinasi',
        'description': 'Kombinasi kulit berminyak di T-zone (dahi, hidung, dagu) dan normal/kering di area pipi.'
    }
}

def init_db():
    """Initialize database with schema and seed data"""
    if not os.path.exists('database'):
        os.makedirs('database')
    
    conn = sqlite3.connect(app.config['DATABASE'])
    
    # Execute schema
    with open('database/schema.sql', 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    
    # Check if data exists
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        # Execute seed data
        with open('database/seed_data.sql', 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
    
    # Check if test users exist
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Create test accounts
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role) 
            VALUES (?, ?, ?, ?)
        """, ('testuser', 'user@test.com', generate_password_hash('user123'), 'user'))
        
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role) 
            VALUES (?, ?, ?, ?)
        """, ('admin', 'admin@test.com', generate_password_hash('admin123'), 'admin'))
    
    conn.commit()
    conn.close()

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def mock_ai_classifier(image_path):
    """Mock AI classifier that simulates skin analysis"""
    # Simulate processing time
    time.sleep(random.uniform(2.0, 3.0))
    
    # Randomly select 1-3 conditions
    all_conditions = list(SKIN_CONDITIONS.keys())
    num_conditions = random.randint(1, 3)
    
    # Smart selection: if kemerahan, higher chance of jerawat or kering
    selected = []
    if random.random() > 0.6 and 'kemerahan' not in selected:
        selected.append('kemerahan')
        # Add related conditions
        if random.random() > 0.5:
            selected.append(random.choice(['jerawat', 'kering']))
    
    # Fill remaining slots
    while len(selected) < num_conditions:
        cond = random.choice(all_conditions)
        if cond not in selected:
            selected.append(cond)
    
    # Generate confidence scores (realistic range)
    results = {}
    for condition in selected:
        confidence = random.randint(65, 98)
        results[condition] = {
            'name': SKIN_CONDITIONS[condition]['name'],
            'description': SKIN_CONDITIONS[condition]['description'],
            'confidence': confidence
        }
    
    # Get recommendations from database
    recommendations = {}
    conn = get_db()
    for condition in selected:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT step_number, step_title, step_description FROM skincare_routines WHERE condition_type = ? ORDER BY step_number",
            (condition,)
        )
        steps = [dict(row) for row in cursor.fetchall()]
        recommendations[condition] = steps
    conn.close()
    
    return results, recommendations

# ============= AUTH ROUTES =============

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email dan password diperlukan'}), 400
    
    email = data['email']
    password = data['password']
    username = data.get('username', email.split('@')[0])
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Email sudah terdaftar'}), 409
    
    # Create user
    password_hash = generate_password_hash(password)
    cursor.execute("""
        INSERT INTO users (username, email, password_hash, role) 
        VALUES (?, ?, ?, ?)
    """, (username, email, password_hash, 'user'))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Create access token
    access_token = create_access_token(
        identity=user_id,
        additional_claims={'role': 'user', 'email': email}
    )
    
    return jsonify({
        'message': 'Registrasi berhasil',
        'token': access_token,
        'user': {
            'id': user_id,
            'email': email,
            'username': username,
            'role': 'user'
        }
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email dan password diperlukan'}), 400
    
    email = data['email']
    password = data['password']
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'Email atau password salah'}), 401
    
    # Create access token
    access_token = create_access_token(
        identity=user['id'],
        additional_claims={'role': user['role'], 'email': user['email']}
    )
    
    return jsonify({
        'token': access_token,
        'user': {
            'id': user['id'],
            'email': user['email'],
            'username': user['username'],
            'role': user['role']
        }
    }), 200

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    user_id = get_jwt_identity()
    claims = get_jwt()
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, role, created_at FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return jsonify({'error': 'User tidak ditemukan'}), 404
    
    return jsonify({
        'id': user['id'],
        'username': user['username'],
        'email': user['email'],
        'role': user['role'],
        'created_at': user['created_at']
    }), 200

@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout (client-side token removal)"""
    return jsonify({'message': 'Logout berhasil'}), 200

# ============= SCAN ROUTES =============

@app.route('/api/upload', methods=['POST'])
@jwt_required()
def upload():
    """Handle photo upload and analysis"""
    user_id = get_jwt_identity()
    
    if 'photo' not in request.files:
        return jsonify({'error': 'Tidak ada foto yang diupload'}), 400
    
    file = request.files['photo']
    if file.filename == '':
        return jsonify({'error': 'Tidak ada file yang dipilih'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Format file tidak didukung. Gunakan JPG, JPEG, atau PNG'}), 400
    
    # Save file with UUID filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    file.save(filepath)
    
    # Resize image for storage optimization
    try:
        img = Image.open(filepath)
        img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
        img.save(filepath, optimize=True, quality=85)
    except Exception as e:
        print(f"Image optimization error: {e}")
    
    # Run mock AI analysis
    conditions, recommendations = mock_ai_classifier(filepath)
    
    # Save to database
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO scans (user_id, photo_path, conditions_detected, confidence_scores, recommendations)
           VALUES (?, ?, ?, ?, ?)""",
        (
            user_id,
            filepath,
            json.dumps(list(conditions.keys())),
            json.dumps({k: v['confidence'] for k, v in conditions.items()}),
            json.dumps(recommendations)
        )
    )
    scan_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'scan_id': scan_id,
        'conditions': conditions,
        'recommendations': recommendations,
        'photo_path': filepath
    })

@app.route('/api/scans/<int:scan_id>', methods=['GET'])
@jwt_required()
def get_scan(scan_id):
    """Get single scan result"""
    user_id = get_jwt_identity()
    claims = get_jwt()
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Admin can view all, user only their own
    if claims['role'] == 'admin':
        cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
    else:
        cursor.execute("SELECT * FROM scans WHERE id = ? AND user_id = ?", (scan_id, user_id))
    
    scan = cursor.fetchone()
    
    if not scan:
        conn.close()
        return jsonify({'error': 'Scan tidak ditemukan'}), 404
    
    # Parse JSON data
    conditions_list = json.loads(scan['conditions_detected'])
    confidence_scores = json.loads(scan['confidence_scores'])
    recommendations = json.loads(scan['recommendations'])
    
    # Rebuild conditions dict
    conditions = {}
    for cond in conditions_list:
        conditions[cond] = {
            'name': SKIN_CONDITIONS[cond]['name'],
            'description': SKIN_CONDITIONS[cond]['description'],
            'confidence': confidence_scores[cond]
        }
    
    # Get recommended products
    cursor.execute("""
        SELECT p.*, 
               COUNT(pr.id) as review_count, 
               COALESCE(AVG(pr.rating), 0) as avg_rating
        FROM products p
        LEFT JOIN product_reviews pr ON p.id = pr.product_id
        WHERE p.id IN (
            SELECT id FROM products 
            ORDER BY RANDOM() 
            LIMIT 6
        )
        GROUP BY p.id
        LIMIT 6
    """)
    products = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'scan': dict(scan),
        'conditions': conditions,
        'recommendations': recommendations,
        'products': products
    })

@app.route('/api/history', methods=['GET'])
@jwt_required()
def api_history():
    """Get scan history"""
    user_id = get_jwt_identity()
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans WHERE user_id = ? ORDER BY scan_date DESC LIMIT 50", (user_id,))
    scans = []
    
    for row in cursor.fetchall():
        scan_dict = dict(row)
        scan_dict['conditions_detected'] = json.loads(scan_dict['conditions_detected'])
        scan_dict['confidence_scores'] = json.loads(scan_dict['confidence_scores'])
        scans.append(scan_dict)
    
    conn.close()
    return jsonify(scans)

# ============= ADMIN ROUTES =============

@app.route('/api/admin/stats', methods=['GET'])
@jwt_required()
def admin_stats():
    """Get admin dashboard stats"""
    claims = get_jwt()
    
    if claims['role'] != 'admin':
        return jsonify({'error': 'Akses ditolak'}), 403
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get stats
    cursor.execute("SELECT COUNT(*) as count FROM scans")
    total_scans = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM products")
    total_products = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM product_reviews")
    total_reviews = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM users")
    total_users = cursor.fetchone()['count']
    
    # Get condition distribution
    cursor.execute("SELECT conditions_detected FROM scans")
    all_conditions = []
    for row in cursor.fetchall():
        all_conditions.extend(json.loads(row['conditions_detected']))
    
    condition_counts = {}
    for cond in all_conditions:
        condition_counts[cond] = condition_counts.get(cond, 0) + 1
    
    # Get recent scans
    cursor.execute("""
        SELECT s.id, s.scan_date, s.conditions_detected, u.username, u.email
        FROM scans s
        LEFT JOIN users u ON s.user_id = u.id
        ORDER BY s.scan_date DESC
        LIMIT 10
    """)
    recent_scans = []
    for row in cursor.fetchall():
        scan = dict(row)
        scan['conditions_detected'] = json.loads(scan['conditions_detected'])
        recent_scans.append(scan)
    
    conn.close()
    
    return jsonify({
        'total_scans': total_scans,
        'total_products': total_products,
        'total_reviews': total_reviews,
        'total_users': total_users,
        'condition_distribution': condition_counts,
        'recent_scans': recent_scans
    })

@app.route('/api/admin/products', methods=['GET'])
@jwt_required()
def admin_get_products():
    """Get all products"""
    claims = get_jwt()
    
    if claims['role'] != 'admin':
        return jsonify({'error': 'Akses ditolak'}), 403
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, COUNT(pr.id) as review_count
        FROM products p
        LEFT JOIN product_reviews pr ON p.id = pr.product_id
        GROUP BY p.id
        ORDER BY p.created_at DESC
    """)
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(products)

@app.route('/api/admin/products', methods=['POST'])
@jwt_required()
def admin_create_product():
    """Create new product"""
    claims = get_jwt()
    
    if claims['role'] != 'admin':
        return jsonify({'error': 'Akses ditolak'}), 403
    
    data = request.get_json()
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (name, brand, category, description, price, bpom_number, active_ingredients)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data['name'],
        data['brand'],
        data['category'],
        data['description'],
        int(data['price']),
        data['bpom_number'],
        data.get('active_ingredients', '')
    ))
    product_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Produk berhasil ditambahkan', 'id': product_id}), 201

@app.route('/api/admin/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def admin_update_product(product_id):
    """Update product"""
    claims = get_jwt()
    
    if claims['role'] != 'admin':
        return jsonify({'error': 'Akses ditolak'}), 403
    
    data = request.get_json()
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products 
        SET name = ?, brand = ?, category = ?, description = ?, 
            price = ?, bpom_number = ?, active_ingredients = ?
        WHERE id = ?
    """, (
        data['name'],
        data['brand'],
        data['category'],
        data['description'],
        int(data['price']),
        data['bpom_number'],
        data.get('active_ingredients', ''),
        product_id
    ))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Produk berhasil diupdate'})

@app.route('/api/admin/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_product(product_id):
    """Delete product"""
    claims = get_jwt()
    
    if claims['role'] != 'admin':
        return jsonify({'error': 'Akses ditolak'}), 403
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM product_reviews WHERE product_id = ?", (product_id,))
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Produk berhasil dihapus'})

@app.route('/api/products/<int:product_id>/reviews', methods=['GET'])
def product_reviews(product_id):
    """Get reviews for a product"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM product_reviews 
        WHERE product_id = ? 
        ORDER BY review_date DESC
    """, (product_id,))
    reviews = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(reviews)

# ============= LEGACY HTML ROUTES (for backward compatibility) =============

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/camera')
def camera():
    """Camera/upload page"""
    return render_template('camera.html')

@app.route('/results/<int:scan_id>')
def results(scan_id):
    """Show analysis results"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
    scan = cursor.fetchone()
    
    if not scan:
        return "Scan tidak ditemukan", 404
    
    # Parse JSON data
    conditions_list = json.loads(scan['conditions_detected'])
    confidence_scores = json.loads(scan['confidence_scores'])
    recommendations = json.loads(scan['recommendations'])
    
    # Rebuild conditions dict
    conditions = {}
    for cond in conditions_list:
        conditions[cond] = {
            'name': SKIN_CONDITIONS[cond]['name'],
            'description': SKIN_CONDITIONS[cond]['description'],
            'confidence': confidence_scores[cond]
        }
    
    # Get recommended products
    cursor.execute("""
        SELECT p.*, 
               COUNT(pr.id) as review_count, 
               COALESCE(AVG(pr.rating), 0) as avg_rating
        FROM products p
        LEFT JOIN product_reviews pr ON p.id = pr.product_id
        WHERE p.id IN (
            SELECT id FROM products 
            ORDER BY RANDOM() 
            LIMIT 6
        )
        GROUP BY p.id
        LIMIT 6
    """)
    products = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('results.html', 
                         scan=dict(scan),
                         conditions=conditions,
                         recommendations=recommendations,
                         products=products)

@app.route('/history')
def history():
    """Scan history page"""
    return render_template('history.html')

@app.route('/admin')
def admin():
    """Admin dashboard"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get stats
    cursor.execute("SELECT COUNT(*) as count FROM scans")
    total_scans = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM products")
    total_products = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM product_reviews")
    total_reviews = cursor.fetchone()['count']
    
    # Get condition distribution
    cursor.execute("SELECT conditions_detected FROM scans")
    all_conditions = []
    for row in cursor.fetchall():
        all_conditions.extend(json.loads(row['conditions_detected']))
    
    condition_counts = {}
    for cond in all_conditions:
        condition_counts[cond] = condition_counts.get(cond, 0) + 1
    
    conn.close()
    
    return render_template('admin.html',
                         total_scans=total_scans,
                         total_products=total_products,
                         total_reviews=total_reviews,
                         condition_counts=condition_counts)

@app.route('/admin/products')
def admin_products():
    """Product list"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, COUNT(pr.id) as review_count
        FROM products p
        LEFT JOIN product_reviews pr ON p.id = pr.product_id
        GROUP BY p.id
        ORDER BY p.created_at DESC
    """)
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return render_template('admin.html', products=products, view='products')

@app.route('/admin/products/new')
def admin_product_new():
    """New product form"""
    return render_template('admin_product_form.html', product=None)

@app.route('/admin/products', methods=['POST'])
def admin_product_create():
    """Create new product"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (name, brand, category, description, price, bpom_number, active_ingredients)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        request.form['name'],
        request.form['brand'],
        request.form['category'],
        request.form['description'],
        int(request.form['price']),
        request.form['bpom_number'],
        request.form.get('active_ingredients', '')
    ))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_products'))

@app.route('/admin/products/<int:product_id>/edit')
def admin_product_edit(product_id):
    """Edit product form"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = dict(cursor.fetchone())
    conn.close()
    
    return render_template('admin_product_form.html', product=product)

@app.route('/admin/products/<int:product_id>/edit', methods=['POST'])
def admin_product_update(product_id):
    """Update product"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products 
        SET name = ?, brand = ?, category = ?, description = ?, 
            price = ?, bpom_number = ?, active_ingredients = ?
        WHERE id = ?
    """, (
        request.form['name'],
        request.form['brand'],
        request.form['category'],
        request.form['description'],
        int(request.form['price']),
        request.form['bpom_number'],
        request.form.get('active_ingredients', ''),
        product_id
    ))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_products'))

@app.route('/admin/products/<int:product_id>/delete', methods=['POST'])
def admin_product_delete(product_id):
    """Delete product"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM product_reviews WHERE product_id = ?", (product_id,))
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_products'))

if __name__ == '__main__':
    init_db()
    print("=" * 60)
    print("WajahKu.id - AI Skin Analysis App")
    print("=" * 60)
    print("Backend API: http://localhost:5000")
    print("JWT Auth: Enabled")
    print("Mock AI Classifier: Active")
    print("Database: SQLite")
    print("=" * 60)
    print("Test Accounts:")
    print("  User: user@test.com / user123")
    print("  Admin: admin@test.com / admin123")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)

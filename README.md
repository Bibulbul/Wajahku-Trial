# WajahKu.id - AI Skin Analysis App

Analisis kulit wajah dengan teknologi AI yang memberikan rekomendasi produk skincare berdasarkan kondisi kulit.

## Fitur

- 📷 Upload/ambil foto wajah untuk analisis
- 🔬 Deteksi kondisi kulit (jerawat, berminyak, kering, kusam, kemerahan, kombinasi)
- 💊 Rekomendasi produk skincare BPOM
- 📊 Riwayat scan
- 🔐 Login dengan role-based access (admin/user)
- 📱 Responsive design

## Tech Stack

**Backend:**
- Python Flask
- SQLite Database
- Flask-JWT-Extended untuk authentication

**Frontend:**
- React + Vite
- React Router
- Axios

## Cara Menjalankan

### Backend (Port 5000)

```bash
# Install dependencies
pip install -r requirements.txt

# Jalankan server
python app.py
```

### Frontend (Port 5173)

```bash
cd frontend

# Install dependencies
npm install

# Jalankan development server
npm run dev
```

### Akses

Buka browser: http://localhost:5173

## Test Accounts

| Email | Password | Role |
|-------|----------|------|
| user@test.com | user123 | User |
| admin@test.com | admin123 | Admin |

## API Endpoints

### Auth
- `POST /api/auth/register` - Register akun baru
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Dapatkan info user (requires token)
- `POST /api/auth/logout` - Logout

### User
- `POST /api/upload` - Upload foto untuk analisis (requires token)
- `GET /api/scans/:id` - Dapatkan hasil scan (requires token)
- `GET /api/history` - Riwayat scan (requires token)

### Admin
- `GET /api/admin/stats` - Statistik dashboard (admin only)
- `GET /api/admin/products` - List produk (admin only)
- `POST /api/admin/products` - Tambah produk (admin only)
- `PUT /api/admin/products/:id` - Update produk (admin only)
- `DELETE /api/admin/products/:id` - Hapus produk (admin only)

## Struktur Project

```
WajahKu_Project/
├── app.py                    # Flask backend
├── requirements.txt          # Python dependencies
├── database/
│   ├── schema.sql           # Database schema
│   └── seed_data.sql        # Sample data
├── frontend/                # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── index.css
│   │   ├── hooks/
│   │   │   └── useAuth.js
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── UserLayout.jsx
│   │   │   │   └── AdminLayout.jsx
│   │   │   └── common/
│   │   │       └── Modal.jsx
│   │   └── pages/
│   │       ├── Login.jsx
│   │       ├── user/
│   │       │   ├── UserHome.jsx
│   │       │   ├── Camera.jsx
│   │       │   ├── Results.jsx
│   │       │   └── History.jsx
│   │       └── admin/
│   │           ├── AdminDashboard.jsx
│   │           └── ProductManagement.jsx
│   ├── vite.config.js
│   └── package.json
└── static/                  # Legacy static files
    └── uploads/            # Uploaded photos
```

## Design

UI menggunakan color palette earthy dan profesional:
- Primary: #2C3E50 (dark slate)
- Secondary: #E8A87C (warm terracotta)
- Accent: #27AE60 (natural green)
- Background: #F5F7FA (soft grey-blue)

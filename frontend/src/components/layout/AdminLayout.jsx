import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import './AdminLayout.css';

const AdminLayout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="admin-layout">
      <aside className="admin-sidebar">
        <div className="sidebar-header">
          <h2>WajahKu Admin</h2>
        </div>
        
        <nav className="sidebar-nav">
          <Link to="/admin/dashboard" className="nav-item">
            <span>📊</span> Dashboard
          </Link>
          <Link to="/admin/products" className="nav-item">
            <span>📦</span> Produk
          </Link>
          <Link to="/admin/settings" className="nav-item">
            <span>⚙️</span> Pengaturan
          </Link>
        </nav>
      </aside>

      <div className="admin-main">
        <header className="admin-topbar">
          <div className="breadcrumbs">
            <span>Admin Panel</span>
          </div>
          
          <div className="topbar-actions">
            <span>{user?.email}</span>
            <button onClick={handleLogout} className="btn-logout">
              Keluar
            </button>
          </div>
        </header>

        <main className="admin-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;

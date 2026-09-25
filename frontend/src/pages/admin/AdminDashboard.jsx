import { useEffect, useState, useCallback } from 'react';
import api from '../../services/api';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = useCallback(async () => {
    try {
      const { data } = await api.get('/admin/stats');
      setStats(data);
    } catch (err) {
      console.error('Error fetching stats:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  if (loading) {
    return <div className="loading-container"><div className="spinner"></div></div>;
  }

  return (
    <div className="admin-dashboard">
      <h1>Dashboard Admin</h1>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <h3>{stats.total_scans}</h3>
            <p>Total Scan</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <h3>{stats.total_users}</h3>
            <p>Total User</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">📦</div>
          <div className="stat-content">
            <h3>{stats.total_products}</h3>
            <p>Total Produk</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">⭐</div>
          <div className="stat-content">
            <h3>{stats.total_reviews}</h3>
            <p>Total Review</p>
          </div>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="conditions-chart">
          <h2>Distribusi Kondisi Kulit</h2>
          <div className="chart-bars">
            {Object.entries(stats.condition_distribution).map(([condition, count]) => {
              const maxCount = Math.max(...Object.values(stats.condition_distribution));
              const percentage = (count / maxCount) * 100;
              
              return (
                <div key={condition} className="chart-bar">
                  <span className="bar-label">{condition}</span>
                  <div className="bar-track">
                    <div className="bar-fill" style={{ width: `${percentage}%` }}></div>
                  </div>
                  <span className="bar-value">{count}</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="recent-scans">
          <h2>Scan Terbaru</h2>
          <div className="scans-table">
            {stats.recent_scans.map((scan) => (
              <div key={scan.id} className="scan-row">
                <div className="scan-user">
                  <strong>{scan.username || scan.email}</strong>
                  <small>{new Date(scan.scan_date).toLocaleString('id-ID')}</small>
                </div>
                <div className="scan-conditions">
                  {scan.conditions_detected.map((cond, idx) => (
                    <span key={idx} className="condition-badge">{cond}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;

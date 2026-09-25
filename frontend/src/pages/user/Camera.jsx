import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import './Camera.css';

const Camera = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    if (!['image/jpeg', 'image/jpg', 'image/png'].includes(file.type)) {
      setError('Format file tidak didukung. Gunakan JPG, JPEG, atau PNG');
      return;
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('Ukuran file terlalu besar. Maksimal 5MB');
      return;
    }

    setSelectedFile(file);
    setError('');

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result);
    };
    reader.readAsDataURL(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('photo', selectedFile);

    try {
      const { data } = await api.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      navigate(`/user/results/${data.scan_id}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Terjadi kesalahan saat mengupload');
      setLoading(false);
    }
  };

  return (
    <div className="camera-page">
      <div className="container">
        <div className="camera-header">
          <h1>Scan Wajah</h1>
          <p>Upload foto wajah untuk mendapatkan analisis kondisi kulit</p>
        </div>

        <div className="camera-container">
          {!preview ? (
            <div className="upload-area" onClick={() => fileInputRef.current?.click()}>
              <div className="upload-icon">📷</div>
              <p>Klik untuk upload foto</p>
              <small>JPG, JPEG, atau PNG (max 5MB)</small>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/jpg,image/png"
                onChange={handleFileSelect}
                style={{ display: 'none' }}
              />
            </div>
          ) : (
            <div className="preview-area">
              <img src={preview} alt="Preview" />
              <div className="preview-actions">
                <button
                  onClick={() => {
                    setPreview(null);
                    setSelectedFile(null);
                  }}
                  className="btn-secondary"
                >
                  Ganti Foto
                </button>
                <button
                  onClick={handleUpload}
                  disabled={loading}
                  className="btn-primary"
                >
                  {loading ? 'Menganalisis...' : 'Analisis Sekarang'}
                </button>
              </div>
            </div>
          )}

          {error && <div className="error-message">{error}</div>}

          {loading && (
            <div className="loading-overlay">
              <div className="spinner"></div>
              <p>AI sedang menganalisis foto Anda...</p>
              <small>Proses ini membutuhkan 2-3 detik</small>
            </div>
          )}
        </div>

        <div className="tips">
          <h3>Tips Foto Terbaik</h3>
          <ul>
            <li>Gunakan pencahayaan yang baik dan merata</li>
            <li>Pastikan wajah menghadap kamera</li>
            <li>Hindari filter atau edit foto</li>
            <li>Gunakan background polos jika memungkinkan</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Camera;

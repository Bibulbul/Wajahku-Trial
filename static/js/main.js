// Camera and Upload Functionality
let stream = null;
let capturedPhoto = null;

const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const preview = document.getElementById('preview');
const previewImage = document.getElementById('previewImage');
const fileInput = document.getElementById('fileInput');
const startCameraBtn = document.getElementById('startCamera');
const captureBtn = document.getElementById('capture');
const stopCameraBtn = document.getElementById('stopCamera');
const analyzeBtn = document.getElementById('analyzeBtn');
const consentCheckbox = document.getElementById('consent');
const loadingOverlay = document.getElementById('loadingOverlay');

// Start Camera
startCameraBtn.addEventListener('click', async () => {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { facingMode: 'user' },
            audio: false 
        });
        
        video.srcObject = stream;
        video.style.display = 'block';
        preview.style.display = 'none';
        previewImage.style.display = 'none';
        
        startCameraBtn.style.display = 'none';
        captureBtn.style.display = 'inline-block';
        stopCameraBtn.style.display = 'inline-block';
    } catch (err) {
        alert('Tidak bisa mengakses kamera. Pastikan izin kamera telah diberikan.');
        console.error('Camera error:', err);
    }
});

// Capture Photo
captureBtn.addEventListener('click', () => {
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);
    
    canvas.toBlob((blob) => {
        capturedPhoto = new File([blob], 'capture.jpg', { type: 'image/jpeg' });
        
        // Show preview
        const url = URL.createObjectURL(blob);
        previewImage.src = url;
        previewImage.style.display = 'block';
        video.style.display = 'none';
        preview.style.display = 'none';
        
        // Stop camera
        stopCamera();
        
        checkAnalyzeButton();
    });
});

// Stop Camera
stopCameraBtn.addEventListener('click', stopCamera);

function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    video.style.display = 'none';
    startCameraBtn.style.display = 'inline-block';
    captureBtn.style.display = 'none';
    stopCameraBtn.style.display = 'none';
}

// File Upload
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        // Validate file type
        if (!['image/jpeg', 'image/jpg', 'image/png'].includes(file.type)) {
            alert('Format file tidak didukung. Gunakan JPG, JPEG, atau PNG.');
            return;
        }
        
        // Validate file size (5MB)
        if (file.size > 5 * 1024 * 1024) {
            alert('Ukuran file terlalu besar. Maksimal 5MB.');
            return;
        }
        
        capturedPhoto = file;
        
        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            previewImage.style.display = 'block';
            preview.style.display = 'none';
            video.style.display = 'none';
        };
        reader.readAsDataURL(file);
        
        checkAnalyzeButton();
    }
});

// Consent Checkbox
consentCheckbox.addEventListener('change', checkAnalyzeButton);

function checkAnalyzeButton() {
    analyzeBtn.disabled = !(capturedPhoto && consentCheckbox.checked);
}

// Analyze Photo
analyzeBtn.addEventListener('click', async () => {
    if (!capturedPhoto) {
        alert('Silakan pilih atau ambil foto terlebih dahulu.');
        return;
    }
    
    if (!consentCheckbox.checked) {
        alert('Silakan setujui consent terlebih dahulu.');
        return;
    }
    
    // Show loading
    loadingOverlay.style.display = 'flex';
    
    // Upload photo
    const formData = new FormData();
    formData.append('photo', capturedPhoto);
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Upload gagal');
        }
        
        const data = await response.json();
        
        // Redirect to results
        window.location.href = `/results/${data.scan_id}`;
    } catch (error) {
        loadingOverlay.style.display = 'none';
        alert('Terjadi kesalahan saat menganalisis foto. Silakan coba lagi.');
        console.error('Upload error:', error);
    }
});

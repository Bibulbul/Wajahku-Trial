// Admin Dashboard Functions

// Initialize charts and data on load
document.addEventListener('DOMContentLoaded', () => {
    // Animate chart bars
    const chartFills = document.querySelectorAll('.chart-fill');
    chartFills.forEach((fill, index) => {
        setTimeout(() => {
            fill.style.opacity = '1';
        }, index * 100);
    });
    
    // Animate stats
    const statValues = document.querySelectorAll('.stat-value, .stat-number');
    statValues.forEach((stat, index) => {
        const value = parseInt(stat.textContent);
        animateValue(stat, 0, value, 1000 + (index * 200));
    });
});

function animateValue(element, start, end, duration) {
    let startTimestamp = null;
    
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const current = Math.floor(progress * (end - start) + start);
        element.textContent = current.toLocaleString('id-ID');
        
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    
    window.requestAnimationFrame(step);
}

// Product management functions
async function loadProductReviews(productId) {
    try {
        const response = await fetch(`/api/products/${productId}/reviews`);
        const reviews = await response.json();
        
        // Display reviews in a modal or section
        console.log('Reviews:', reviews);
        return reviews;
    } catch (error) {
        console.error('Error loading reviews:', error);
    }
}

// Form validation for product form
const productForm = document.querySelector('.product-form');
if (productForm) {
    productForm.addEventListener('submit', (e) => {
        const bpomInput = document.getElementById('bpom_number');
        const bpomValue = bpomInput.value.trim();
        
        // Validate BPOM format (NA followed by digits)
        if (!bpomValue.match(/^NA\d+$/)) {
            e.preventDefault();
            alert('Format nomor BPOM tidak valid. Harus dimulai dengan "NA" diikuti angka.');
            bpomInput.focus();
            return false;
        }
        
        return true;
    });
    
    // Live preview update
    const formInputs = productForm.querySelectorAll('input, select, textarea');
    formInputs.forEach(input => {
        input.addEventListener('input', updateProductPreview);
    });
}

function updateProductPreview() {
    const preview = document.querySelector('.product-preview .product-card');
    if (!preview) return;
    
    const name = document.getElementById('name').value;
    const brand = document.getElementById('brand').value;
    const price = document.getElementById('price').value;
    const bpom = document.getElementById('bpom_number').value;
    
    if (name) {
        preview.querySelector('h3').textContent = name;
    }
    if (brand) {
        preview.querySelector('.product-brand').textContent = brand;
        const placeholder = preview.querySelector('.product-placeholder');
        if (placeholder) {
            placeholder.textContent = brand.substring(0, 2) + name.substring(0, 2);
        }
    }
    if (price) {
        const formatted = parseInt(price).toLocaleString('id-ID');
        preview.querySelector('.product-price').textContent = `Rp ${formatted}`;
    }
    if (bpom) {
        preview.querySelector('.product-bpom small').textContent = `BPOM: ${bpom}`;
    }
}

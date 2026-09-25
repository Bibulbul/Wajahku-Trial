// Load History
async function loadHistory() {
    const historyList = document.getElementById('historyList');
    const emptyState = document.getElementById('emptyState');
    
    try {
        const response = await fetch('/api/history');
        const scans = await response.json();
        
        historyList.innerHTML = '';
        
        if (scans.length === 0) {
            historyList.style.display = 'none';
            emptyState.style.display = 'block';
            return;
        }
        
        scans.forEach(scan => {
            const item = createHistoryItem(scan);
            historyList.appendChild(item);
        });
        
    } catch (error) {
        console.error('Error loading history:', error);
        historyList.innerHTML = '<p style="text-align:center; color: var(--danger);">Gagal memuat riwayat.</p>';
    }
}

function createHistoryItem(scan) {
    const item = document.createElement('div');
    item.className = 'history-item';
    
    const date = new Date(scan.scan_date);
    const formattedDate = date.toLocaleDateString('id-ID', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    const conditions = scan.conditions_detected;
    const conditionTags = conditions.map(c => 
        `<span class="tag">${c}</span>`
    ).join('');
    
    item.innerHTML = `
        <img src="/${scan.photo_path}" alt="Scan" class="history-thumbnail" onerror="this.style.display='none'">
        <div class="history-info">
            <h3>Scan Kulit</h3>
            <p class="history-date">${formattedDate}</p>
            <div class="condition-tags">
                ${conditionTags}
            </div>
        </div>
        <a href="/results/${scan.id}" class="btn btn-primary">Lihat Detail</a>
    `;
    
    return item;
}

// Load on page load
document.addEventListener('DOMContentLoaded', loadHistory);

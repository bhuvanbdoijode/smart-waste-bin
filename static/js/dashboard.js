// Dashboard Real-time Updates
let refreshInterval;

function initDashboard(isAdmin) {
    loadBinsData();
    // Auto-refresh every 3 seconds
    refreshInterval = setInterval(loadBinsData, 3000);
}

function loadBinsData() {
    fetch('/api/bins')
        .then(response => response.json())
        .then(data => {
            updateStatistics(data.stats);
            updateBinsTable(data.bins, isAdmin);
        })
        .catch(error => {
            console.error('Error loading bins data:', error);
        });
}

function updateStatistics(stats) {
    document.getElementById('stat-total').textContent = stats.total;
    document.getElementById('stat-full').textContent = stats.full;
    document.getElementById('stat-half').textContent = stats.half;
    document.getElementById('stat-empty').textContent = stats.empty;
}

function updateBinsTable(bins, isAdmin) {
    const tbody = document.getElementById('bins-tbody');
    
    if (bins.length === 0) {
        tbody.innerHTML = '<tr><td colspan="' + (isAdmin ? '7' : '6') + '" class="text-center">No bins found. Add a bin to get started.</td></tr>';
        return;
    }
    
    tbody.innerHTML = bins.map(bin => {
        const statusClass = getStatusClass(bin.fill_level);
        const statusText = getStatusText(bin.fill_level);
        const progressClass = getProgressClass(bin.fill_level);
        const lastUpdated = formatDateTime(bin.last_updated);
        
        let actionsHtml = '';
        if (isAdmin) {
            actionsHtml = `
                <td>
                    <div class="btn-group btn-group-sm" role="group">
                        <a href="/bins/edit/${bin.id}" class="btn btn-warning" title="Edit">
                            <i class="bi bi-pencil"></i>
                        </a>
                        <button onclick="deleteBin('${bin.id}', '${bin.location}')" class="btn btn-danger" title="Delete">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            `;
        }
        
        return `
            <tr>
                <td><strong>${bin.id.substring(0, 8)}</strong></td>
                <td>${bin.location}</td>
                <td><span class="badge bg-secondary">${bin.type || 'General'}</span></td>
                <td>
                    <div class="progress">
                        <div class="progress-bar ${progressClass}" role="progressbar" 
                             style="width: ${bin.fill_level}%" 
                             aria-valuenow="${bin.fill_level}" aria-valuemin="0" aria-valuemax="100">
                            ${bin.fill_level}%
                        </div>
                    </div>
                </td>
                <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                <td><small>${lastUpdated}</small></td>
                ${actionsHtml}
            </tr>
        `;
    }).join('');
}

function getStatusClass(level) {
    if (level >= 80) return 'status-full';
    if (level >= 50) return 'status-half';
    return 'status-empty';
}

function getStatusText(level) {
    if (level >= 80) return 'FULL';
    if (level >= 50) return 'HALF FULL';
    return 'EMPTY';
}

function getProgressClass(level) {
    if (level >= 80) return 'bg-danger';
    if (level >= 50) return 'bg-warning';
    return 'bg-success';
}

function formatDateTime(isoString) {
    if (!isoString) return 'N/A';
    const date = new Date(isoString);
    return date.toLocaleString();
}

function deleteBin(binId, location) {
    if (confirm(`Are you sure you want to delete bin at "${location}"?`)) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/bins/delete/' + binId;
        document.body.appendChild(form);
        form.submit();
    }
}

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});

// -------------------- WEBCAM CAPTURE DETECTION --------------------

const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const captureBtn = document.getElementById("captureBtn");

// Start webcam
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function(stream) {
            video.srcObject = stream;
            video.play();
        });
}

// Capture image
captureBtn.addEventListener("click", function () {
    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL("image/jpeg");

    // Send to Flask
    fetch("/detect_webcam", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: "image_data=" + encodeURIComponent(imageData),
    })
    .then(() => {
        alert("Detection completed! Dashboard will update.");
        location.reload();
    });
});

// -------------------- FCM PUSH NOTIFICATIONS (SINGLE ADMIN DEVICE) --------------------
if ("Notification" in window && firebase.messaging) {
    const messaging = firebase.messaging();

    navigator.serviceWorker.register("/firebase-messaging-sw.js").then(function (registration) {

        // ASK PERMISSION
        Notification.requestPermission().then(async function (permission) {
            if (permission !== "granted") {
                console.log("Notifications not allowed.");
                return;
            }

            try {
                const vapidKey = "BM0iOGuKXHCkjmGrLTQX_6vYr7dnuZzPQV872vJkVCrgOQFbEd0iybJsC0vhvvxNEfkxnK1cSyR3jPhbbxpC4vQ";

                // No messaging.useServiceWorker() needed in compat mode
                const token = await messaging.getToken({ vapidKey: vapidKey });

                if (token) {
                    console.log("FCM Token:", token);

                    // SAVE TOKEN TO BACKEND
                    fetch("/save_fcm_token", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ token: token }),
                    });
                } else {
                    console.log("No token received.");
                }

            } catch (error) {
                console.error("Error getting FCM token:", error);
            }
        });
    });
}

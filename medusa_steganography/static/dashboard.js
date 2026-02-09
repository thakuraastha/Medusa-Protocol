// Dashboard Interactive Features for Medusa Protocol

// Notification System
function showDashboardNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `dashboard-notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        <span>${message}</span>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('show');
    }, 100);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Table Row Click Handler
document.addEventListener('DOMContentLoaded', function() {

    // Add click handlers to action buttons
    const viewButtons = document.querySelectorAll('.btn-icon[title="View"], .btn-icon[title="View Records"]');
    viewButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            showDashboardNotification('Opening record viewer...', 'info');
        });
    });

    const downloadButtons = document.querySelectorAll('.btn-icon[title="Download"]');
    downloadButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            showDashboardNotification('Downloading file...', 'success');
        });
    });

    const imageButtons = document.querySelectorAll('.btn-icon[title="View Images"]');
    imageButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            showDashboardNotification('Loading medical images...', 'info');
        });
    });

    const prescribeButtons = document.querySelectorAll('.btn-icon[title="Prescribe"]');
    prescribeButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            showDashboardNotification('Opening prescription form...', 'info');
        });
    });

    // Action buttons in cards
    const actionButtons = document.querySelectorAll('.action-btn');
    actionButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const actionText = this.querySelector('span').textContent;
            showDashboardNotification(`${actionText} - Feature coming soon!`, 'info');
        });
    });

    // Appointment action buttons
    const joinButtons = document.querySelectorAll('.btn-small.btn-primary');
    joinButtons.forEach(btn => {
        if (btn.textContent.includes('Join')) {
            btn.addEventListener('click', function() {
                showDashboardNotification('Connecting to video consultation...', 'success');
            });
        }
    });

    const notesButtons = document.querySelectorAll('.btn-small');
    notesButtons.forEach(btn => {
        if (btn.textContent.includes('Notes')) {
            btn.addEventListener('click', function() {
                showDashboardNotification('Opening patient notes...', 'info');
            });
        }
    });

    // Highlight table rows on hover for better UX
    const tableRows = document.querySelectorAll('.medical-table tbody tr');
    tableRows.forEach(row => {
        row.style.cursor = 'pointer';
        row.addEventListener('click', function(e) {
            // Don't trigger if clicking on a button
            if (!e.target.closest('.btn-icon')) {
                const patientId = this.querySelector('td:first-child').textContent;
                showDashboardNotification(`Selected patient ${patientId}`, 'info');
            }
        });
    });

    // Add interactive hover effects to stat cards
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        card.style.cursor = 'pointer';
        card.addEventListener('click', function() {
            const label = this.querySelector('.stat-label').textContent;
            showDashboardNotification(`Viewing details for: ${label}`, 'info');
        });
    });

    // Diagnosis cards click handlers
    const diagnosisCards = document.querySelectorAll('.diagnosis-card');
    diagnosisCards.forEach(card => {
        card.style.cursor = 'pointer';
        card.addEventListener('click', function() {
            const header = this.querySelector('h4').textContent;
            showDashboardNotification(`Viewing ${header}...`, 'info');
        });
    });

    // Info card rows
    const infoRows = document.querySelectorAll('.info-row');
    infoRows.forEach(row => {
        row.style.cursor = 'pointer';
        row.addEventListener('click', function() {
            const label = this.querySelector('.info-label').textContent;
            const value = this.querySelector('.info-value').textContent;
            showDashboardNotification(`${label} ${value}`, 'info');
        });
    });

    // Add loading animation to table rows
    const addLoadingAnimation = (element) => {
        element.style.opacity = '0.5';
        setTimeout(() => {
            element.style.opacity = '1';
        }, 500);
    };

    // Search functionality (if search input exists)
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            tableRows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // Add real-time clock
    function updateClock() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        const dateString = now.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        const clockElement = document.querySelector('.dashboard-clock');
        if (clockElement) {
            clockElement.innerHTML = `
                <div class="clock-time">${timeString}</div>
                <div class="clock-date">${dateString}</div>
            `;
        }
    }

    // Update clock every second
    if (document.querySelector('.dashboard-clock')) {
        setInterval(updateClock, 1000);
        updateClock();
    }

    // Badge animations
    const badges = document.querySelectorAll('.badge, .status');
    badges.forEach(badge => {
        badge.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1)';
        });
        badge.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });

    // Appointment cards interaction
    const appointmentCards = document.querySelectorAll('.appointment-card');
    appointmentCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.borderLeftWidth = '6px';
        });
        card.addEventListener('mouseleave', function() {
            this.style.borderLeftWidth = '4px';
        });
    });

    console.log('Medusa Protocol Dashboard initialized successfully');
});

// Add notification styles dynamically
const style = document.createElement('style');
style.textContent = `
    .dashboard-notification {
        position: fixed;
        top: -100px;
        right: 20px;
        background: var(--bg-card);
        border: 2px solid var(--border);
        border-left: 4px solid var(--primary);
        color: var(--text-primary);
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: var(--shadow-lg);
        display: flex;
        align-items: center;
        gap: 12px;
        z-index: 10000;
        transition: top 0.3s ease;
        min-width: 300px;
        max-width: 400px;
    }

    .dashboard-notification.show {
        top: 20px;
    }

    .dashboard-notification.success {
        border-left-color: var(--success);
    }

    .dashboard-notification.success i {
        color: var(--success);
    }

    .dashboard-notification.error {
        border-left-color: var(--danger);
    }

    .dashboard-notification.error i {
        color: var(--danger);
    }

    .dashboard-notification.info {
        border-left-color: var(--primary);
    }

    .dashboard-notification.info i {
        color: var(--primary);
    }

    .dashboard-notification i {
        font-size: 20px;
    }

    .dashboard-notification span {
        flex: 1;
        font-weight: 500;
    }

    .badge, .status {
        transition: transform 0.2s ease;
    }

    .appointment-card {
        transition: all 0.3s ease;
    }

    .dashboard-clock {
        background: var(--bg-darker);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 15px 20px;
        text-align: center;
    }

    .clock-time {
        font-size: 24px;
        font-weight: 700;
        color: var(--primary);
        margin-bottom: 5px;
    }

    .clock-date {
        font-size: 12px;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
`;
document.head.appendChild(style);

// Export functions for use in other scripts
window.dashboardUtils = {
    showNotification: showDashboardNotification
};

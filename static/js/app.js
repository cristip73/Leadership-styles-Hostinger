// Main JavaScript for Management Style Assessment

// Initialize tooltips and popovers if Bootstrap is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-info)');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.add('fade');
            setTimeout(() => alert.remove(), 150);
        }, 5000);
    });
});

// Utility function for API calls
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(endpoint, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'API call failed');
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Form validation helper
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Show loading overlay
function showLoading(message = 'Se încarcă...') {
    const loadingHtml = `
        <div id="loadingOverlay" class="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center" style="background: rgba(0,0,0,0.5); z-index: 9999;">
            <div class="text-center text-white">
                <div class="spinner-border mb-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <div>${message}</div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', loadingHtml);
}

// Hide loading overlay
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.remove();
    }
}

// Smooth scroll to element
function scrollToElement(element) {
    element.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
    });
}

// Export functionality for supervisor dashboard
function exportResults(format) {
    window.location.href = `/api/export/${format}`;
}

// Print results
function printResults() {
    window.print();
}

// Session timeout warning (30 minutes)
let sessionTimeout;
function resetSessionTimeout() {
    clearTimeout(sessionTimeout);
    sessionTimeout = setTimeout(() => {
        if (confirm('Sesiunea dvs. va expira curând. Doriți să continuați?')) {
            // Refresh session
            fetch('/').then(() => resetSessionTimeout());
        }
    }, 28 * 60 * 1000); // 28 minutes
}

// Initialize session timeout on page load
if (document.querySelector('#assessmentSection')) {
    resetSessionTimeout();
    document.addEventListener('click', resetSessionTimeout);
    document.addEventListener('keypress', resetSessionTimeout);
}

// Keyboard navigation for assessment
document.addEventListener('keydown', function(e) {
    if (document.querySelector('#assessmentSection')) {
        // Arrow keys for navigation
        if (e.key === 'ArrowLeft') {
            const prevBtn = document.querySelector('.question-slide:not([style*="display: none"]) .btn-prev:not([disabled])');
            if (prevBtn) prevBtn.click();
        } else if (e.key === 'ArrowRight') {
            const nextBtn = document.querySelector('.question-slide:not([style*="display: none"]) .btn-next:not([disabled])');
            if (nextBtn) nextBtn.click();
        }
        
        // Number keys for answer selection
        if (e.key >= '1' && e.key <= '4') {
            const answerMap = {'1': 'A', '2': 'B', '3': 'C', '4': 'D'};
            const answer = answerMap[e.key];
            const currentQuestion = document.querySelector('.question-slide:not([style*="display: none"])');
            if (currentQuestion) {
                const radio = currentQuestion.querySelector(`input[value="${answer}"]`);
                if (radio) {
                    radio.checked = true;
                    radio.dispatchEvent(new Event('change'));
                }
            }
        }
    }
});

// Add animation class to cards on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '0';
            entry.target.style.transform = 'translateY(20px)';
            setTimeout(() => {
                entry.target.style.transition = 'all 0.6s ease';
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }, 100);
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe all cards for animation
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.card').forEach(card => {
        observer.observe(card);
    });
});

// Console message
console.log('%c Management Style Assessment System ', 'background: #0066cc; color: white; padding: 5px 10px; border-radius: 3px;');
console.log('Version 1.0.0 - Flask/Gunicorn Edition');
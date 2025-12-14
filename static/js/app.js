// ===============================
// Flood Relief System - Main JS
// ===============================

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function () {
    console.log('%c🌊 Flood Relief System Loaded', 'color:#0b61ff;font-size:18px;font-weight:bold');

    // Initialize Mobile Navigation
    initMobileNav();

    // Initialize Flash Messages (auto-hide)
    initFlashMessages();

    // Initialize Form Enhancements
    initFormEnhancements();

    // Initialize Table Features
    initTableFeatures();

    // Initialize Number Animations
    initNumberAnimations();
});

// ===============================
// Mobile Navigation Toggle
// ===============================
function initMobileNav() {
    const navToggle = document.getElementById('navToggle');
    const navList = document.getElementById('navList');

    if (!navToggle || !navList) return;

    navToggle.addEventListener('click', function () {
        const isOpen = navList.classList.contains('nav__list--open');
        
        if (isOpen) {
            navList.classList.remove('nav__list--open');
            navToggle.setAttribute('aria-expanded', 'false');
        } else {
            navList.classList.add('nav__list--open');
            navToggle.setAttribute('aria-expanded', 'true');
        }
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', function (e) {
        if (!navToggle.contains(e.target) && !navList.contains(e.target)) {
            navList.classList.remove('nav__list--open');
            navToggle.setAttribute('aria-expanded', 'false');
        }
    });

    // Close mobile menu when clicking on a nav link
    const navLinks = navList.querySelectorAll('.nav__link');
    navLinks.forEach(link => {
        link.addEventListener('click', function () {
            navList.classList.remove('nav__list--open');
            navToggle.setAttribute('aria-expanded', 'false');
        });
    });
}

// ===============================
// Flash Messages
// ===============================
function initFlashMessages() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        // Add close button if it doesn't exist
        if (!alert.querySelector('.alert__close')) {
            const closeBtn = document.createElement('button');
            closeBtn.className = 'alert__close';
            closeBtn.innerHTML = '×';
            closeBtn.setAttribute('aria-label', 'Close alert');
            closeBtn.style.fontSize = '1.5rem';
            closeBtn.style.lineHeight = '1';
            
            closeBtn.addEventListener('click', function () {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 300);
            });
            
            alert.appendChild(closeBtn);
        }

        // Auto-hide after 5 seconds
        setTimeout(() => {
            alert.style.transition = 'opacity 300ms';
            alert.style.opacity = '0';
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 300);
        }, 5000);
    });
}

// ===============================
// Form Enhancements
// ===============================
function initFormEnhancements() {
    // File input display
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function (e) {
            const fileName = e.target.files[0]?.name;
            if (fileName) {
                console.log('📁 File selected:', fileName);
                
                // Create or update file name display
                let fileNameDisplay = input.nextElementSibling;
                if (!fileNameDisplay || !fileNameDisplay.classList.contains('file-name-display')) {
                    fileNameDisplay = document.createElement('div');
                    fileNameDisplay.className = 'file-name-display';
                    fileNameDisplay.style.marginTop = '8px';
                    fileNameDisplay.style.fontSize = '0.875rem';
                    fileNameDisplay.style.color = '#6b7280';
                    input.parentNode.insertBefore(fileNameDisplay, input.nextSibling);
                }
                fileNameDisplay.textContent = `Selected: ${fileName}`;
            }
        });
    });

    // Form submission handling
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            
            // Check if file input exists and is empty
            const fileInput = form.querySelector('input[type="file"]');
            if (fileInput && fileInput.hasAttribute('required') && !fileInput.files.length) {
                e.preventDefault();
                alert('Please select a file to upload');
                return;
            }

            // Add loading state to submit button
            if (submitBtn) {
                const originalText = submitBtn.textContent;
                submitBtn.textContent = 'Loading...';
                submitBtn.disabled = true;
                
                // Re-enable after 5 seconds (fallback)
                setTimeout(() => {
                    submitBtn.textContent = originalText;
                    submitBtn.disabled = false;
                }, 5000);
            }
        });
    });
}

// ===============================
// Table Features
// ===============================
function initTableFeatures() {
    // Add hover effect info for table rows
    const tableRows = document.querySelectorAll('.table tbody tr');
    tableRows.forEach(row => {
        row.style.cursor = 'pointer';
        row.style.transition = 'background-color 200ms';
    });

    // Make entire row clickable if it contains a link
    tableRows.forEach(row => {
        const link = row.querySelector('a.btn');
        if (link) {
            row.addEventListener('click', function (e) {
                // Don't trigger if clicking the link itself
                if (e.target.tagName !== 'A' && e.target.tagName !== 'BUTTON') {
                    link.click();
                }
            });
        }
    });
}

// ===============================
// Number Animations
// ===============================
function initNumberAnimations() {
    const metrics = document.querySelectorAll('.metric__value');
    
    // Check if we're on a page with metrics
    if (metrics.length === 0) return;

    // Simple number animation
    metrics.forEach(metric => {
        const text = metric.textContent;
        const numberMatch = text.match(/[\d,]+/);
        
        if (!numberMatch) return;

        const finalNumber = parseInt(numberMatch[0].replace(/,/g, ''));
        if (isNaN(finalNumber) || finalNumber === 0) return;

        const prefix = text.split(numberMatch[0])[0].trim();
        const suffix = text.split(numberMatch[0])[1]?.trim() || '';

        let currentNumber = 0;
        const increment = Math.ceil(finalNumber / 50);
        const duration = 1000;
        const stepTime = duration / 50;

        const timer = setInterval(() => {
            currentNumber += increment;
            if (currentNumber >= finalNumber) {
                currentNumber = finalNumber;
                clearInterval(timer);
            }
            
            const formattedNumber = currentNumber.toLocaleString();
            metric.textContent = `${prefix} ${formattedNumber} ${suffix}`.trim();
        }, stepTime);
    });
}

// ===============================
// Utility Functions
// ===============================

/**
 * Format number with commas
 */
function formatNumber(num) {
    return num.toLocaleString();
}

/**
 * Format currency in PKR
 */
function formatCurrency(num) {
    return `PKR ${num.toLocaleString()}`;
}

/**
 * Show a notification message
 */
function showNotification(message, type = 'info') {
    const container = document.querySelector('.container');
    if (!container) return;

    const alert = document.createElement('div');
    alert.className = `alert alert--${type}`;
    alert.style.position = 'fixed';
    alert.style.top = '80px';
    alert.style.right = '20px';
    alert.style.maxWidth = '400px';
    alert.style.zIndex = '9999';
    alert.style.animation = 'slideIn 300ms ease-out';
    
    alert.innerHTML = `
        <div class="alert__content">
            <p class="alert__message">${message}</p>
        </div>
        <button class="alert__close" onclick="this.parentElement.remove()">×</button>
    `;

    document.body.appendChild(alert);

    // Auto-remove after 4 seconds
    setTimeout(() => {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 300);
    }, 4000);
}

/**
 * Smooth scroll to element
 */
function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

/**
 * Debounce function for search/filter inputs
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ===============================
// Export for global use
// ===============================
window.floodRelief = {
    formatNumber,
    formatCurrency,
    showNotification,
    scrollToElement,
    debounce
};

// Add slide-in animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);
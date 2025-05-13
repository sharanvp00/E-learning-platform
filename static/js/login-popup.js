// Login Popup Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check if the URL contains the login_required parameter
    const urlParams = new URLSearchParams(window.location.search);
    const loginRequired = urlParams.get('login_required');
    
    if (loginRequired === 'true') {
        // Show the login popup
        showLoginPopup();
        
        // Remove the parameter from the URL without refreshing the page
        const newUrl = window.location.pathname;
        window.history.replaceState({}, document.title, newUrl);
    }
    
    // Close popup when clicking outside or on close button
    document.addEventListener('click', function(event) {
        const popup = document.getElementById('login-popup');
        const closeBtn = document.getElementById('close-popup');
        
        if (popup && (event.target === popup || event.target === closeBtn)) {
            closeLoginPopup();
        }
    });
});

function showLoginPopup() {
    // Create popup container if it doesn't exist
    if (!document.getElementById('login-popup')) {
        const popup = document.createElement('div');
        popup.id = 'login-popup';
        popup.className = 'login-popup';
        
        popup.innerHTML = `
            <div class="login-popup-content">
                <span id="close-popup" class="close-popup">&times;</span>
                <div class="popup-icon">
                    <i class="fas fa-lock"></i>
                </div>
                <h2>Login Required</h2>
                <p>You need to be logged in to access this page.</p>
                <div class="popup-buttons">
                    <a href="/login/" class="btn-login">Login Now</a>
                    <a href="/register/" class="btn-register">Register</a>
                </div>
            </div>
        `;
        
        document.body.appendChild(popup);
        
        // Add animation class after a small delay to trigger animation
        setTimeout(() => {
            popup.classList.add('show');
        }, 10);
    }
}

function closeLoginPopup() {
    const popup = document.getElementById('login-popup');
    if (popup) {
        popup.classList.remove('show');
        
        // Remove the popup from DOM after animation completes
        setTimeout(() => {
            popup.remove();
        }, 300);
    }
}
document.addEventListener('DOMContentLoaded', () => {
    const errorDiv = document.getElementById('login-error');

    if (errorDiv && errorDiv.textContent.trim() !== '') {
        // Retirer et remettre la classe pour forcer l'animation
        errorDiv.classList.remove('animate-shake');
        void errorDiv.offsetWidth; // force reflow
        errorDiv.classList.add('animate-shake');
    }

    // Toggle mot de passe
    const toggleBtn = document.getElementById('login-toggle-password');
    const passwordInput = document.getElementById('login-password');
    toggleBtn?.addEventListener('click', () => {
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            toggleBtn.innerHTML = '<i class="fas fa-eye-slash"></i>';
        } else {
            passwordInput.type = 'password';
            toggleBtn.innerHTML = '<i class="fas fa-eye"></i>';
        }
    });
});

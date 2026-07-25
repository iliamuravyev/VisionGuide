document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.querySelector('.login-form');
    
    if (!loginForm) return;

    loginForm.addEventListener('submit', function(e) {
        let isValid = true;
        const inputs = this.querySelectorAll('input[required]');

        inputs.forEach(input => {
            const group = input.closest('.input-group');
            if (!input.value.trim()) {
                group.classList.add('error');
                isValid = false;
            } else {
                group.classList.remove('error');
            }
        });

        if (!isValid) {
            e.preventDefault();
        }
        else {
            window.location.href = "templates/index2.html"
        }
    });

    const inputs = loginForm.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            const group = this.closest('.input-group');
            if (this.value.trim()) {
                group.classList.remove('error');
            }
        });
    });
});

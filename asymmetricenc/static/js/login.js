const container = document.querySelector('.container');
const registerBtn = document.querySelector('.register-btn');
const loginBtn = document.querySelector('.login-btn');

registerBtn.addEventListener('click', () => {
    container.classList.add('active');
});

loginBtn.addEventListener('click', () => {
    container.classList.remove('active');
});

// Handle login form submit
const loginForm = document.querySelector('#login-form'); // make sure your form has id="login-form"

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.querySelector('#username1').value;
    const password = document.querySelector('#password1').value;

    try {
        const res = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                form_type: 'login',
                username1: username,
                password1: password
            })
        });

        if (res.ok) {
            const data = await res.json();
            if (data.success && data.redirect) {
                window.location.href = data.redirect; // navigate to chat.html
            } else {
                alert(data.error || 'Login failed');
            }
        } else {
            const err = await res.json();
            alert(err.error || 'Login error');
        }
    } catch (err) {
        console.error(err);
        alert('Network error, please try again.');
    }
});

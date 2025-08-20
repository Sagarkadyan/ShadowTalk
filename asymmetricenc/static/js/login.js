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

document.getElementById('login-form').addEventListener('submit', async function(e){
    e.preventDefault();

    const data = Object.fromEntries(new FormData(this).entries());

    try {
        const resp = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await resp.json();

        if (result.success && result.redirect) {
            window.location.href = result.redirect;   // ✅ Go to /chat
        } else {
            alert(result.error || "Login failed.");
        }
    } catch (err) {
        console.error(err);
        alert("Network error. Try again.");
    }
});

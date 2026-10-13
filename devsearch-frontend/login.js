import { API_BASE } from "./config.js";

let loginUser = () => {
    let form = document.getElementById('login-form')

    form.addEventListener('submit', (e) => {
        e.preventDefault()
        
        let formData = {
            'username': form.username.value,
            'password': form.password.value
        }

        fetch(`${API_BASE}/api/users/token/`, {
            method:'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            let token = data.access
            console.log(token)

            if (token) {
                localStorage.setItem('token', token)
                window.location = 'projects-list.html'
            } else {
                alert('Incorrect username or password!')
            }

        })

    })
}

loginUser()
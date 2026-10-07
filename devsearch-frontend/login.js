let loginUser = () => {
    let form = document.getElementById('login-form')

    form.addEventListener('submit', (e) => {
        e.preventDefault()
        
        let formData = {
            'username': form.username.value,
            'password': form.password.value
        }

        fetch('http://127.0.0.1:8000/api/users/token/', {
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
                window.location = 'file:///C:/Users/DELL/Desktop/2026/Dev/devsearch/devsearch-frontend/projects-list.html'
            } else {
                alert('Incorrect username or password!')
            }

        })

    })
}

loginUser()
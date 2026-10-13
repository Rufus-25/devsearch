import { API_BASE } from "./config.js";

function escapeHtml(text) {
    const div = document.createElement('div')
    div.textContent = text ?? ''
    return div.innerHTML
}

function imageSrc(path) {
    if (!path) return `${API_BASE}/static/images/default.jpg`
    return path.startsWith('http') ? path : `${API_BASE}${path}`
}

let projectsUrl = `${API_BASE}/api/projects/`
let projectsWrapper = document.querySelector('#projects--wrapper')

let token = localStorage.getItem('token')
let loginBtn = document.getElementById('login-btn')
let logoutBtn = document.getElementById('logout-btn')

if (token) {
    loginBtn.remove()
} else {
    logoutBtn.remove()
}

logoutBtn.addEventListener('click', (e) => {
    e.preventDefault()

    localStorage.removeItem('token')
    alert('You are now logged out!')
})



let getProjects = () => {

    fetch(projectsUrl)
        .then(response => response.json())
        .then(data => {
            console.log(data)
            buildProjects(data)
        })

}

let buildProjects = (projects) => {
    projectsWrapper.innerHTML = ''

    for (let i=0; i < projects.length; i++) {

        let project = projects[i]

        let projectHtml = `
        <div class="single-project">
            <img src="${imageSrc(project.project_image)}" class="project-image" />
            <h2>${escapeHtml(project.title)}</h2>
            <p>${escapeHtml((project.description || '').substring(0, 180))}...</p>
            <p><em>Vote Ratio: ${project.vote_ratio}%</em></p>
            <span class="vote-btn" data-projectid="${project.id}" data-votetype="up"> + </span>
            <span class="vote-btn" data-projectid="${project.id}" data-votetype="down"> - </span>
        </div>
        `

        projectsWrapper.innerHTML += projectHtml;
    }

    voteProject()
}

let voteProject = () => {
    let voteBtns = document.getElementsByClassName('vote-btn')

    for(let i=0; i<voteBtns.length; i++) {

        voteBtns[i].addEventListener('click', (e) => {
            let projectId = e.target.dataset.projectid
            let voteType = e.target.dataset.votetype
            
            fetch(`${API_BASE}/api/projects/${projectId}/vote/`, {
                method:'POST',
                headers: {
                    'Content-Type':'application/json',
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({'value':voteType})
            })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data)

                getProjects()
            })
        })
    }
}

getProjects()
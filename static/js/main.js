// Pagination + Search Form working together
let searchForm = document.getElementById('searchForm')
let pageLinks = document.getElementsByClassName('page--link')

if (searchForm) {
for(let i=0; i < pageLinks.length; i++) {
    pageLinks[i].addEventListener('click', function (e) {
    e.preventDefault()
    
    let page = this.dataset.page
    searchForm.innerHTML += `<input name="page" value="${page}" hidden />`
    searchForm.submit()
    })
}
}


let tags = document.getElementsByClassName('project-tag')

for (let i = 0; tags.length > i; i++) {
    // tags[i].addEventListener('click', (e) => {
    //     let tagId = e.target.dataset.tag
    //     let projectId = e.target.dataset.project

    //     fetch('http://127.0.0.1:8000/api/remove-tag/', {
    //         method:'DELETE',
    //         headers: {
    //             'Content-Type':'application/json'
    //         },
    //         body: JSON.stringify({'tag':tagId, 'project':projectId})
    //     })
    //     .then(response => response.json())
    //     .then(data => {
    //         e.target.remove()
    //     })
    // })

    tags[i].addEventListener('click', (e) => {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value
        fetch(e.target.dataset.url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken},
            body: JSON.stringify({'tag': e.target.dataset.tag, 'project': e.target.dataset.project})
        })
        .then(response => {
            if (!response.ok) throw new Error()
            e.target.remove()          // only after the server confirms
        })
        .catch(() => alert('Could not remove tag.'))
    })
}
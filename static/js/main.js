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

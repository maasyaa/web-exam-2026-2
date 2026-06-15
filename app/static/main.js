'use strict';

function imagePreviewHandler(event) {
    if (event.target.files && event.target.files[0]) {
        let reader = new FileReader();
        reader.onload = function (e) {
            let img = document.querySelector('.background-preview > img');
            img.src = e.target.result;
            if (img.classList.contains('d-none')) {
                let label = document.querySelector('.background-preview > label');
                label.classList.add('d-none');
                img.classList.remove('d-none');
            }
        }
        reader.readAsDataURL(event.target.files[0]);
    }
}

function openLink(event) {
    let row = event.target.closest('.row');
    if (row && row.dataset.url) {
        window.location = row.dataset.url;
    }
}

window.onload = function() {
    for (let bookElm of document.querySelectorAll('.books-list .row')) {
        bookElm.onclick = function(event) {
            let row = event.target.closest('.row');
            if (row && row.dataset.url) {
                window.location = row.dataset.url;
            }
        };
    }
};
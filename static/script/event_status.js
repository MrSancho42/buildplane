const button = document.querySelectorAll('.event__js-submit');

button.forEach(button => {
    button.addEventListener('click', send_data);
})

function send_data() {
    if (this.dataset.status === 'true'){
        this.classList.remove('event__submit_done');
        this.dataset.status = 'false';
    } else {
        this.classList.add('event__submit_done');
        this.dataset.status = 'true';
    }

    var dict = {
        status: (this.dataset.status === 'true'),
        event: this.dataset.event
    };

    fetch(`${location.pathname}/event_status`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(dict),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
}
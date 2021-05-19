const button = document.querySelectorAll('.task__js-submit');

button.forEach(button => {
    button.addEventListener('click', foo);
})

function foo() {
    if (this.dataset.status === 'true'){
        this.classList.remove('task__submit_done');
        this.dataset.status = 'false';
    } else {
        this.classList.add('task__submit_done');
        this.dataset.status = 'true';
    }

    var dict = {
        status: (this.dataset.status === 'true'),
        task: this.parentElement.dataset.task
    };

    fetch(`${location.pathname}/task_status`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(dict),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
}
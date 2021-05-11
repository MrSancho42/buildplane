const button = document.querySelectorAll('.task__submit');

button.forEach(button => {
    button.addEventListener('click', foo);
})

function foo() {
    console.log(this.dataset.status)
    if (this.dataset.status === 'true'){
        console.log('Виконано');
        this.classList.remove('task__submit_done');
        this.dataset.status = 'false';
    } else {
        this.classList.add('task__submit_done');
        this.dataset.status = 'true';
        console.log('Не виконано');
    }
}
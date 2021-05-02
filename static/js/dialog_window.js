(function() {
    let dialogButton = document.getElementsByClassName('form-settings__delete-button')[0];
    let dialogWindow = document.getElementsByClassName('dialog-box')[0];

    dialogButton.addEventListener('click', () => {
        dialogWindow.classList.add('dialog-box__active')
        dialogWindow.showModal();

        let greenButton = document.getElementsByClassName('dialog-box__green-button')[0];
        let redButton = document.getElementsByClassName('dialog-box__red-button')[0];
    
        greenButton.addEventListener('click', () => {
            dialogWindow.classList.remove('dialog-box__active')
        })
    
        redButton.addEventListener('click', () => {
            dialogWindow.classList.remove('dialog-box__active')
        })
    })
})();

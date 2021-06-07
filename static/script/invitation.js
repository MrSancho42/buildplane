const submit = document.querySelectorAll(".invitation__js-submit");
const deny = document.querySelectorAll(".invitation__js-deny");

submit.forEach(submit => {
	submit.addEventListener('click', () => {send(true, submit)});
});

deny.forEach(deny => {
	deny.addEventListener('click', () => {send(false, deny)});
});

function send(status, hui) {
	
	var dict = {
        status: status,
		command: hui.parentElement.dataset.command
	};

	fetch(`${location.pathname}/invitation`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(dict),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
}

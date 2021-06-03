const del = document.querySelectorAll(".invitation__js-delete");

del.forEach(del => {
	del.addEventListener('click', () => {send(del)});
});

function send(hui) {
	
	var dict = {
		command: hui.parentElement.dataset.command,
        user_id: hui.parentElement.dataset.user_id
	};

	fetch(`/invitation_del`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(dict),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
}
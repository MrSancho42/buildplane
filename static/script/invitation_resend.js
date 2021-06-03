const resend = document.querySelectorAll(".invitation__js-resend");

resend.forEach(resend => {
	resend.addEventListener('click', () => {send(resend)});
});

function send(hui) {
	
	var dict = {
		command: hui.parentElement.dataset.command,
        user_id: hui.parentElement.dataset.user_id
	};

	fetch(`/invitation_resend`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(dict),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
}
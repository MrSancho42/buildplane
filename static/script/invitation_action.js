const del = document.querySelectorAll(".invitation__js-delete");
const resend = document.querySelectorAll(".invitation__js-resend");

del.forEach(del => {
	del.addEventListener('click', () => {send(del, `/invitation_del`)});
});

resend.forEach(resend => {
	resend.addEventListener('click', () => {send(resend, `/invitation_resend`)});
});

function send(el, myPath) {
	
	var dict = {
		command: el.dataset.command,
        user_id: el.dataset.user_id
	};

	fetch(myPath, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(dict),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
}

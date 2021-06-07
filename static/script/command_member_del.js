const member = document.querySelectorAll(".member-item__js-delete");

member.forEach(member => {
	member.addEventListener('click', () => {member_del(member)});
});

function member_del(hui) {
	
	var dict = {
		command: hui.dataset.command,
        user_id: hui.dataset.user_id
	};

	fetch(`/command_member_del`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(dict),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
}
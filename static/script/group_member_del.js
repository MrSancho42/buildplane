const member = document.querySelectorAll(".member-item__js-delete");

member.forEach(member => {
	member.addEventListener('click', () => {member_del(member)});
});

function member_del(element) {
	
	var dict = {
		group: element.dataset.group,
        user_id: element.dataset.user_id
	};

	fetch('/group_member_del', {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(dict),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
}
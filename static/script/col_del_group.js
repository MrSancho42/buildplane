const delButtn = document.querySelectorAll(".cols-item__js-delete");

delButtn.forEach(delButtn => {
	delButtn.addEventListener('click', () => {col_del(delButtn)});
});

function col_del(element) {

	var dict = {
        col_id: element.dataset.col,
        group_id: element.dataset.group_id
	};

	fetch(`/group_col_del`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(dict),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
}
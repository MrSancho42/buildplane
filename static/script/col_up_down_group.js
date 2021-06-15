const upButtn = document.querySelectorAll(".cols-item__js-up");
const downButtn = document.querySelectorAll(".cols-item__js-down");

upButtn.forEach(upButtn => {
	upButtn.addEventListener('click', () => {col_change(upButtn, true)});
});
downButtn.forEach(downButtn => {
	downButtn.addEventListener('click', () => {col_change(downButtn, false)});
});

function col_change(element, status) {

	var dict = {
        col_id: element.parentElement.dataset.col,
        group_id: element.parentElement.dataset.group_id, 
        status: status
	};

	fetch(`/group_change_col_status`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(dict),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
}
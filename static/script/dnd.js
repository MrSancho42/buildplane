const drag_zone = document.querySelectorAll('.drop-zone');
const drag_item = document.querySelectorAll('.drag-item');

drag_item.forEach(drag_item => {
	drag_item.addEventListener('dragstart', dragstart);
	drag_item.addEventListener('dragend', dragend);
})

drag_zone.forEach(drag_zone => {
	drag_zone.addEventListener('dragenter', (event) => {
		event.preventDefault();
	});
	drag_zone.addEventListener('dragleave', dragleave);
	drag_zone.addEventListener('dragover', dragover);
	drag_zone.addEventListener('drop', drop);
})

let current_item = null
function dragstart () {
	current_item = this
	this.classList.add('drag-item_active');
}

function dragend () {
	this.classList.remove('drag-item_active');
	current_item = null
}

function dragleave () {
	this.classList.remove('drop-zone_active');
}
function dragover (event) {
	event.preventDefault();
	if (current_item.parentElement !== this) {
		this.classList.add('drop-zone_active');
	}
}
function drop () {
	if (current_item.parentElement !== this) {
		this.classList.remove('drop-zone_active');
		this.append(current_item);
		send_data(this.dataset.coll, current_item.dataset.task)
	}
}

function send_data (coll, task) {
    var dict = {
        coll: coll,
        task: task
    };
	
	
    console.log('zone', coll);
    console.log('item', task);
	console.log(location.pathname);

    fetch(`${location.pathname}/dnd`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(dict),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
}
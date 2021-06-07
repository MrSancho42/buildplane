function hide_left_bar(button) {
	const left_bar = document.getElementsByClassName('left-bar')[0];
	if (document.getElementsByClassName('work-area__bar')) {
		var work_area__bar = document.getElementsByClassName('work-area__bar')[0];		
	}

	if (button.dataset.status === 'true') {
		left_bar.classList.add('left-bar_hidden');
		button.classList.add('left-bar__minimize_hidden');

		if (typeof work_area__bar !== 'undefined') {
			work_area__bar.classList.add('work-area__bar_hidden');
		}

		button.dataset.status = 'false';
	}
	else {
		left_bar.classList.remove('left-bar_hidden');
		button.classList.remove('left-bar__minimize_hidden');

		if (typeof work_area__bar !== 'undefined') {
			work_area__bar.classList.remove('work-area__bar_hidden');
		}

		button.dataset.status = 'true';
	}
}
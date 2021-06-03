import sqlite3
from flask import Flask, render_template, g, redirect, url_for, request, flash, session, abort, jsonify, make_response
from flask_session import Session
import redis
from datetime import timedelta
from re import search as research

import config
from db_work import db_work
import wtform as wtf
from os.path import normcase, dirname, abspath


"""
Головний скрипт додатку.
Обробляє всі запити.
"""


def get_path(f):
	"""
	Приймає шлях до файлу.
	Повертає повний нормалізований шлях до нього,
	відштовхуючись від місця запуску коду.
	"""
	return normcase(dirname(abspath(__file__)) + f)


app = Flask(__name__)

app.config['SESSION_TYPE'] = 'redis' #	Встановлення типу сесії
app.config['SECRET_KEY'] = config.SECRET_KEY #	Встановлення секретного ключа із config.py
app.config['SESSION_PERMANENT'] = False #	Встановлення запам'ятовування сесії
app.config['SESSION_USE_SIGNER'] = False #	Вимагання підпису сеансу?
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=31) #	Час життя сеансу
app.config['SESSION_KEY_PREFIX'] = 'session:' #  Префікс для ключів сесії у Redis 
app.config['SESSION_MEMCACHED'] = redis.Redis(host=config.HOST, port='6379', password=config.SECRET_KEY) # Підключення до Redis

Session(app)



db = None
@app.before_request
def before_request():
	"""
	Функція що спрацьовує перед запитом.

	Спершу перевіряється чи не завантажується файл, якщо так, то подальше
	виконання функції припиняється.

	Потім первіряє чи користувач авторизований,
	якщо ні - то його переадресовує на /login.
	Це спрацьовує для усіх запитів, окрім винятків.

	Після цього іде підключення до БД. та створення глобальної змінної
	для взаємодії із нею. id користувача передається тут же.
	"""

	if research('/static/', request.path):
		return

	exceptions = ['/', '/login', '/registration']
	if 'user' not in session and request.path not in exceptions:
		return redirect(url_for('login'))

	if not hasattr(g, 'link_db'):
		g.link_db = sqlite3.connect(get_path(config.DATABASE))
		g.link_db.row_factory = sqlite3.Row
	global db
	db = db_work(g.link_db.cursor(), session.get('user'))

	#Перевірка належності до команди
	if research('/command/', request.path):
		if research('/command/add', request.path):
			return
		if not db.get_membership('command', request.path.split('/')[2]):
			abort(404)

	#Перевірка належності до групи
	if research('/group/', request.path):
		if research('/group/add', request.path):
			return
		if not db.get_membership('group', request.path.split('/')[2]):
			abort(404)


@app.teardown_appcontext
def close_db(error):
	"""
	Функція що спрацьовує після запиту.
	Закриває підключення до БД.
	"""

	if hasattr(g, 'link_db'):
		g.link_db.commit()
		g.link_db.close()


#Тимчасові сторінки///////////////////////////////////////////////////////////
@app.route('/session', methods=["POST", "GET"])
def get_session():
	"""
	Сторінка сесій.
	"""

	user = db.get_user()
	if not user:
		flash('Авторизованих користувачів немає...')
		return render_template('session.html')

	permanent = session['_permanent']

	if request.method == 'POST':
		session.clear()
		return render_template('session.html')

	return render_template('session.html', user=user, permanent=permanent)


@app.route('/date', methods=["POST", "GET"])
def date():
	if request.method == 'POST':
		date = request.form['date']

		if not date:
			flash(f'Ну і чому нічого не послав?')
			return render_template('date.html')

		flash(f'input date: {date}')

		date = db.to_timestamp(date)
		flash(f'timestamp: {date}')

		date = db.from_timestamp(date)
		flash(f'output date: {date}')

	return render_template('date.html')


#Перші сторінки///////////////////////////////////////////////////////////////
@app.route('/')
def main():
	"""
	Головна сторінка.
	"""

	return render_template('main.html')


@app.route('/login', methods=["POST", "GET"])
def login():
	"""
	Сторінка авторизації.
	"""

	form = wtf.login_form()

	if form.validate_on_submit():
		keys = [key for key in session if key != 'csrf_token']
		for key in keys:
			session.pop(key)

		res = db.login(form.login.data, form.psw.data)
		if res['status']:
			session.permanent = form.remember.data
			session['user'] = res['user']
			return redirect(url_for('home'))

		flash(res['message'])

	return render_template('login.html', form=form)


@app.route('/registration', methods=["POST", "GET"])
def registration():
	"""
	Сторінка реєстрації
	"""

	form = wtf.reg_form()

	if form.validate_on_submit():
		if db.registration(form.login.data, form.psw.data, form.name.data):
			return redirect(url_for('login'))

		flash('Такий логін уже існує')

	return render_template('registration.html', form=form)


#Користувач///////////////////////////////////////////////////////////////////
@app.route('/home/task')
def home():
	"""
	Головна сторінка користувача
	"""

	user = db.get_user()

	commands = db.get_commands()
	if commands:
		for i in commands:
			i['ownership'] = i['owner_id'] == session['user']
			i.pop('owner_id')

	cols = db.get_personal_tasks()

	invitations = db.get_incoming_invitation()

	return render_template('home.html',
							user=user,
							commands=commands,
							cols=cols,
							invitations=invitations)


@app.route('/home/task/dnd', methods=["POST"])
def home_dnd():
	"""
	Функція яка отримує дані при перетягуванні персональних завдань.
	"""

	data = request.get_json()

	db.set_personal_task_col(data['coll'], data['task'])

	return make_response(jsonify({}, 200))


@app.route('/home/task/invitation', methods=["POST"])
def home_invitation():
	"""
	Обробник надходжених запрошень на вступ до команди
	"""

	data = request.get_json()
	print(data)
	if data['status']: # якщо натиснута кнопка "прийняти"
		db.add_user_to_command(data['command'])

	else: # якщо натиснута кнопка "відхилити"
		db.change_invitation_status(data['command'])

	return redirect(url_for('home'))


@app.route('/home/task/task_status', methods=["POST"])
def home_task_status():
	"""
	Функція що отримує дані при зміні стану персонального завдання.
	"""

	data = request.get_json()

	db.set_personal_task_status(data['status'], data['task'])

	return make_response(jsonify({}, 200))


#Команди//////////////////////////////////////////////////////////////////////
@app.route('/command/add', methods=["POST", "GET"])
def add_command():
	"""
	Сторінка створення нової команди
	"""

	user = db.get_user()
	user_id = user['user_id']
	form = wtf.add_command_form()

	if form.validate_on_submit():
		if db.add_command(form.name.data, user_id):
			return redirect(url_for('home'))

	return render_template('add_command.html', form=form, user=user)


@app.route('/command/<int:command_id>/settings', methods=["GET", "POST"])
def settings_command(command_id):
	"""
	Сторінка налаштувань команди
	"""

	user = db.get_user()
	command = db.get_command_info(command_id)

	if db.get_owner_rights(command_id, 'command'):
		name = db.get_command_info(command_id)['name']
		form = wtf.edit_command_form(name=name)
		form_dialog = wtf.del_dialog_form()

		return render_template('edit_command.html', user=user, command_id=command_id,
								form=form, form_dialog=form_dialog, name=name,
								command=command)
	else: abort(404)


@app.route('/command/<int:command_id>/edit', methods=["GET", "POST"])
def edit_command(command_id):
	"""
	Функція редагування команди
	"""

	name = db.get_command_info(command_id)['name']
	form = wtf.edit_command_form(name=name)
	form_dialog = wtf.del_dialog_form()

	if form.validate_on_submit():
		name = form.name.data
		if db.edit_command(command_id, name):
			return redirect(url_for('settings_command', command_id=command_id))

	abort(404) # якщо користувач прописав шлях сам


@app.route('/command/<int:command_id>/del', methods=["GET", "POST"])
def del_command(command_id):
	"""
	Функція видалення команди
	"""

	try:
		name = db.get_command_info(command_id)['name']
		form = wtf.edit_command_form(name=name)
		form_dialog = wtf.del_dialog_form()
	except TypeError: #якщо команда уже видалена
		abort(404)

	if form_dialog.submit.data:
		db.del_command(command_id)
		return redirect(url_for('home'))

	# при натисненні "НІ" у діалоговому вікні
	if request.method == 'POST':
		return redirect(url_for('settings_command', command_id=command_id))

	abort(404) # якщо користувач прописав шлях сам


@app.route('/command/<command_id>/task')
def command_task(command_id):
	"""
	Сторінка завдань команди.
	"""

	user = db.get_user()
	is_owner = db.get_owner_rights(command_id, 'command')

	command = db.get_command_info(command_id)

	groups = groups_ownership(command_id)

	cols = db.get_command_tasks(command_id)
	return render_template('command_task.html',
							user=user,
							is_owner=is_owner,
							command=command,
							groups=groups,
							cols=cols)


@app.route('/command/<command_id>/task-group')
def command_task_group(command_id):
	"""
	Сторінка завдань команди.
	"""

	user = db.get_user()
	is_owner = db.get_owner_rights(command_id, 'command')

	command = db.get_command_info(command_id)

	groups = groups_ownership(command_id)

	cols = db.get_command_tasks_group(command_id)
	return render_template('command_task_group.html',
							user=user,
							is_owner=is_owner,
							command=command,
							groups=groups,
							cols=cols)


@app.route('/command/<command_id>/task-user')
def command_task_user(command_id):
	"""
	Сторінка завдань команди із відібраними завданнями  користувача.
	"""

	user = db.get_user()
	is_owner = db.get_owner_rights(command_id, 'command')

	command = db.get_command_info(command_id)

	groups = groups_ownership(command_id)

	cols = db.get_command_tasks_user(command_id)
	return render_template('command_task_user.html',
							user=user,
							is_owner=is_owner,
							command=command,
							groups=groups,
							cols=cols)


@app.route('/command/<command_id>/<mod>/dnd', methods=["POST"])
def command_task_dnd(command_id, mod):
	"""
	Функція яка отримує дані при перетягуванні завдань команди.
	"""

	data = request.get_json()

	db.set_command_task_col(data['coll'], data['task'], command_id)
	return make_response(jsonify({}, 200))


@app.route('/command/<command_id>/<mod>/task_status', methods=["POST"])
def command_task_status(command_id, mod):
	"""
	Функція що отримує дані при зміні стану завдання команди.
	"""

	data = request.get_json()

	db.set_task_status(data['status'], data['task'], 'command', command_id)

	return make_response(jsonify({}, 200))


@app.route('/command/<command_id>/members', methods=["POST", "GET"])
def command_members(command_id):
	"""
	Сторінка перегляду і запрошення користувачів до команди
	"""

	if db.get_owner_rights(command_id, 'command'):
		user = db.get_user()
		command = db.get_command_info(command_id)
		form = wtf.add_member_form()

		rejected_invitations = db.get_sended_invitation(command_id, 0)
		sended_invitations = db.get_sended_invitation(command_id, 1)
		members = db.get_command_members(command_id)

		if form.validate_on_submit():
			login = form.login.data
			flash(db.check_send_nice_invitation(login, command_id))

		return render_template('members_command.html', user=user, command=command,
								form=form, rejected_invitations=rejected_invitations,
								sended_invitations=sended_invitations, members=members)
	else: abort(403)


@app.route('/invitation_resend', methods=["POST", "GET"])
def invitation_resend():
	"""
	Функція повторного надсилання запрошення

	Використовується на сторінці /command/<command_id>/members
	"""

	data = request.get_json()
	db.change_invitation_status(data['command'], data['user_id'])

	return redirect(url_for('home'))


@app.route('/invitation_del', methods=["POST", "GET"])
def invitation_del():
	"""
	Функція повторного видалення запрошення

	Використовується на сторінці /command/<command_id>/members
	"""

	data = request.get_json()
	db.del_invitation(data['command'], data['user_id'])

	return redirect(url_for('home'))


#Групи////////////////////////////////////////////////////////////////////////
def groups_ownership(command_id):
	"""
	Функція що дістає групи команди та визначає чи користувач є їх власником

	Повертає список груп
	"""

	groups = db.get_groups(command_id)

	if groups:
		for group in groups:
			group['ownership'] = group['user_id'] in [group['owner_id'], group['command_owner_id']]
			group.pop('owner_id')
			group.pop('command_owner_id')

	return groups


@app.route('/group/<group_id>/task')
def group_task(group_id):
	"""
	Сторінка завдань групи.
	"""

	user = db.get_user()
	current_group = db.get_group_info(group_id)
	# нижче рядок перевіряє, чи є користувач власником команди
	# необхідно для кнопки створення групи
	is_owner = db.get_owner_rights(current_group['command_id'], 'command')
	is_group_owner = db.get_owner_rights(group_id, 'group')

	command = db.get_command_info(current_group['command_id'])

	groups = groups_ownership(current_group['command_id'])

	cols = db.get_group_tasks(group_id)
	return render_template('group_task.html',
							user=user,
							is_owner=is_owner,
							is_group_owner=is_group_owner,
							command=command,
							current_group=current_group,
							groups=groups,
							cols=cols)


@app.route('/group/<group_id>/task-user')
def group_task_user(group_id):
	"""
	Сторінка завдань користувача у групі.
	"""

	user = db.get_user()
	current_group = db.get_group_info(group_id)
	# нижче рядок перевіряє, чи є користувач власником команди
	# необхідно для кнопки створення групи
	is_owner = db.get_owner_rights(current_group['command_id'], 'command')
	is_group_owner = db.get_owner_rights(group_id, 'group')

	command = db.get_command_info(current_group['command_id'])

	groups = groups_ownership(current_group['command_id'])

	cols = db.get_group_tasks_user(group_id)
	return render_template('group_task_user.html',
							user=user,
							is_owner=is_owner,
							is_group_owner=is_group_owner,
							command=command,
							current_group=current_group,
							groups=groups,
							cols=cols)


@app.route('/group/<group_id>/<mod>/dnd', methods=["POST"])
def group_task_dnd(group_id, mod):
	"""
	Функція яка отримує дані при перетягуванні завдань групи.
	"""

	data = request.get_json()

	db.set_group_task_col(data['coll'], data['task'], group_id)
	return make_response(jsonify({}, 200))


@app.route('/group/add', methods=["POST", "GET"])
def add_group():
	"""
	Сторінка створення нової групи
	"""

	command_id = request.args.get('command_id')
	if command_id == None: # якщо самовільний перехід на /group/add
		abort(404)

	command = db.get_command_info(command_id)
	user = db.get_user()
	if not db.get_owner_rights(command_id, 'command'):
		abort(403)

	list_owners = db.get_users_in_command(command_id) # для випадаючого списку вибору власника
	form = wtf.add_group_form()
	form.owner.choices = list_owners

	if not form.color.data: # встановлення кольору за замовчуванням
		form.color.data = "#bccbff"

	if form.validate_on_submit():
		name = form.name.data
		color = form.color.data
		owner = form.owner.data
		blocked = form.blocked.data

		group_id = db.add_group(name, color, command_id, owner, user['user_id'], blocked)

		# перевірка, чи той, хто створив, є власником групи
		if user['user_id'] != int(owner):
			return redirect(url_for('command_task', command_id=command_id))

		return redirect(url_for('group_task', group_id=group_id))

	return render_template('add_group.html', form=form, user=user,
						command=command)


@app.route('/group/<int:group_id>/settings', methods=["GET", "POST"])
def settings_group(group_id):
	"""
	Сторінка налаштувань групи
	"""

	user = db.get_user_login()
	group = db.get_full_group_info(group_id)

	if db.get_edit_group_rights(user['user_id'], group['group_id']):
		command = db.get_command_info(group['command_id'])
		list_owners = db.get_users_in_command(group['command_id']) # для випадаючого списку вибору власника

		form = wtf.edit_group_form(request.form)

		# формування списку для призначення власника
		form.owner.choices = list_owners # це список [(user_id, user_name)]
		# визначення власника в списку за замовчуванням - того, що є зараз власником
		default_owner = 0
		for i in list_owners:
			if i[1] == user['login']:
				default_owner = i[0]
				break

		form.owner.default = default_owner
		form.process() # без цього рядок вище не хоче працювати
		form.color.data = group['color']
		form.name.data = group['name']
		form.blocked.data = group['blocked']
		form_dialog = wtf.del_dialog_form()

		return render_template('edit_group.html', user=user, group_id=group_id, command=command,
								form=form, form_dialog=form_dialog, group=group)
	else: abort(403)


@app.route('/group/<int:group_id>/edit', methods=["POST", "GET"])
def edit_group(group_id):
	"""
	Функція редагування групи
	"""

	form = wtf.edit_group_form(request.form)

	if form.validate_on_submit():
		name = form.name.data
		owner_id = form.owner.data
		blocked = form.blocked.data
		color = form.color.data

		db.edit_group(group_id, name, owner_id, blocked, color)
		return redirect(url_for('settings_group', group_id=group_id))

	abort(403) # якщо користувач прописав шлях сам



@app.route('/group/<int:group_id>/del', methods=["GET", "POST"])
def del_group(group_id):
	"""
	Функція видалення групи
	"""

	try:
		group = db.get_group_info(group_id)
		command_id = group['command_id']
		form_dialog = wtf.del_dialog_form()
	except TypeError: #якщо команда уже видалена
		abort(404)
	
	if form_dialog.submit.data:
		db.del_group(group_id)
		return redirect(url_for('command_task', command_id=command_id))

	# при натисненні "НІ" у діалоговому вікні
	if request.method == 'POST':
		return redirect(url_for('settings_group', group_id=group_id))

	abort(404) # якщо користувач прописав шлях сам


@app.route('/group/<group_id>/<mod>/task_status', methods=["POST"])
def group_task_status(group_id, mod):
	"""
	Функція що отримує дані при зміні стану завдання групи.
	"""

	data = request.get_json()

	db.set_task_status(data['status'], data['task'], 'group', group_id)

	return make_response(jsonify({}, 200))


if __name__ == '__main__':
	app.run(host=config.HOST, debug=config.DEBUG)

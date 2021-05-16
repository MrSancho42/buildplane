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

	return render_template('home.html',
							user=user,
							commands=commands,
							cols=cols)


@app.route('/home/task/dnd', methods=["POST"])
def home_dnd():
	"""
	Функція яка отримує дані при перетягуванні персональних завдань.
	"""

	data = request.get_json()

	db.set_personal_task_col(data['coll'], data['task'])

	return make_response(jsonify({}, 200))


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
	user_id = user['user_id']
	command = db.get_command_info(command_id)

	if db.get_owner_rights(command_id, user_id, 'command'):
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
	is_owner = db.get_owner_rights(command_id, user['user_id'], 'command')

	command = db.get_command_info(command_id)

	groups = groups_ownership(command_id)

	cols = db.get_command_tasks(command_id)
	return render_template('command_task.html',
							user=user,
							is_owner=is_owner,
							command=command,
							groups=groups,
							cols=cols)


@app.route('/command/<command_id>/task/dnd', methods=["POST"])
def command_task_dnd(command_id):
	"""
	Функція яка отримує дані при перетягуванні завдань команди.
	"""

	data = request.get_json()

	db.set_command_task_col(data['coll'], data['task'], command_id)
	return make_response(jsonify({}, 200))


@app.route('/command/<command_id>/task/task_status', methods=["POST"])
def command_task_status(command_id):
	"""
	Функція що отримує дані при зміні стану завдання команди.
	"""

	data = request.get_json()

	db.set_task_status(data['status'], data['task'], 'command', command_id)

	return make_response(jsonify({}, 200))


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

	command = db.get_command_info(current_group['command_id'])

	groups = groups_ownership(current_group['command_id'])

	cols = db.get_group_tasks(group_id)
	return render_template('group_task.html',
							user=user,
							command=command,
							current_group=current_group,
							groups=groups,
							cols=cols)


@app.route('/group/<group_id>/task/dnd', methods=["POST"])
def group_task_dnd(group_id):
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
	command = db.get_command_info(command_id)
	user = db.get_user()
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

		group_id = db.add_group(name, color, command_id, owner, blocked)
		return redirect(url_for('group_task', group_id=group_id))

	return render_template('add_group.html', form=form, user=user,
						command=command)
@app.route('/group/<group_id>/task/task_status', methods=["POST"])
def group_task_status(group_id):
	"""
	Функція що отримує дані при зміні стану завдання групи.
	"""

	data = request.get_json()

	db.set_task_status(data['status'], data['task'], 'group', group_id)

	return make_response(jsonify({}, 200))


if __name__ == '__main__':
	app.run(host=config.HOST, debug=config.DEBUG)

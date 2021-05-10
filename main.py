import sqlite3
from flask import Flask, render_template, g, redirect, url_for, request, flash, session, jsonify, make_response
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


@app.teardown_appcontext
def close_db(error):
	"""
	Функція що спрацьовує після запиту.
	Закриває підключення до БД.
	"""

	if hasattr(g, 'link_db'):
		g.link_db.commit()
		g.link_db.close()


@app.route('/clear')
def clear():
	"""
	Тимчасова функція для очищення сесії.
	"""
	
	session.clear()
	return redirect(url_for('main'))


@app.route('/')
def main():
	"""
	Головна сторінка.
	"""

	print('Користувач', session.get('user'))
	print(session.keys(), session.values())
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
		print(session)

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
	data = request.get_json()

	db.set_personal_task_col(data['coll'], data['task'])

	return make_response(jsonify({}, 200))


def groups_ownership(command_id):
	groups = db.get_groups(command_id)

	if groups:
		for group in groups:
			group['ownership'] = group['user_id'] in [group['owner_id'], group['command_owner_id']]
			group.pop('owner_id')
			group.pop('command_owner_id')
	
	return groups


@app.route('/command/<command_id>/task')
def command_task(command_id):
	user = db.get_user()
	command = db.get_command_name(command_id)
	
	groups = groups_ownership(command_id)

	cols = db.get_command_tasks(command_id)
	return render_template('command_task.html',
							user=user,
							command=command,
							groups=groups,
							cols=cols)


@app.route('/command/<command_id>/task/dnd', methods=["POST"])
def command_task_dnd(command_id):
	data = request.get_json()
	
	db.set_command_task_col(data['coll'], data['task'], command_id)
	return make_response(jsonify({}, 200))


@app.route('/group/<group_id>/task')
def group_task(group_id):
	user = db.get_user()
	current_group = db.get_group_info(group_id)
	
	command = db.get_command_name(current_group['command_id'])
	
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
	data = request.get_json()
	
	db.set_group_task_col(data['coll'], data['task'], group_id)
	return make_response(jsonify({}, 200))


if __name__ == '__main__':
	app.run(host=config.HOST, debug=config.DEBUG)

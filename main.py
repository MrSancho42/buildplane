import sqlite3
from flask import Flask, render_template, g, redirect, url_for, request, flash, session
from werkzeug.datastructures import MultiDict
from datetime import timedelta

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
app.config['SECRET_KEY'] = config.SECRET_KEY
app.permanent_session_lifetime = timedelta(days=60)


db = None
@app.before_request
def before_request():
	exceptions = ['/', '/login', '/registration']
	if 'user' not in session and request.path not in exceptions:
		#return redirect(url_for('login'))
		pass

	if not hasattr(g, 'link_db'):
		g.link_db = sqlite3.connect(get_path(config.DATABASE))
		g.link_db.row_factory = sqlite3.Row
	global db
	db = db_work(g.link_db.cursor(), session)


@app.teardown_appcontext
def close_db(error):
	if hasattr(g, 'link_db'):
		g.link_db.commit()
		g.link_db.close()


@app.route('/clear')
def clear():
	session.clear()
	return redirect(url_for('main'))


@app.route('/')
def main():
	print('Користувач', session.get('user'))
	print(session.keys(), session.values())
	return render_template('main.html')


@app.route('/login', methods=["POST", "GET"])
def login():
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
	form = wtf.reg_form()

	if form.validate_on_submit():
		if db.registration(form.login.data, form.psw.data, form.name.data):
			return redirect(url_for('login'))
			
		flash('Такий логін уже існує')
			
	return render_template('registration.html', form=form)

@app.route('/add_command', methods=["POST", "GET"])
def add_command():
	form = wtf.add_command_form()

	if form.validate_on_submit():
		if db.add_command(form.name.data, session['user']['user_id']):
			if 'commands' in session:
				session.pop('commands')
			render_template('home.html', user=session['user'])
		else:
			print("shos' pizda")

	return render_template('add_command.html', form=form, user=session['user'])

@app.route('/home/task')
def home():
	"""
	Головна сторінка користувача
	"""
	if 'commands' in session:
		print(session['commands'])
	if 'commands' not in session:
		commands = db.get_commands()
		for i in commands:
			i['ownership'] = i['owner_id'] == session['user']['user_id']
			i.pop('owner_id')

		session['commands'] = commands
	print(session['commands'])
	
	cols = db.get_cols('user', session['user']['user_id'])
	if cols:
		cols = db.get_personal_tasks(cols)
	
	return render_template('home.html',
							user=session['user'],
							commands=session['commands'],
							cols=cols)


@app.route('/settings_command/<int:command_id>', methods=["GET", "POST"])
def settings_command(command_id):
	"""
	Сторінка налаштувань команди
	"""
	name = db.get_command_name(command_id)
	form = wtf.edit_command_form(name=name)
	form_dialog = wtf.del_dialog_form()

	return render_template('edit_command.html', user=session['user'], command_id=command_id,
							form=form, form_dialog=form_dialog, name=name)


@app.route('/edit_command/<int:command_id>', methods=["GET", "POST"])
def edit_command(command_id):
	"""
	Функція редагування команди
	"""
	print('edit')
	name = db.get_command_name(command_id)
	form = wtf.edit_command_form(name=name)
	form_dialog = wtf.del_dialog_form()

	if form.validate_on_submit():
		print('Підтвердити')
	return redirect(url_for('settings_command', command_id=command_id))


@app.route('/del_command/<int:command_id>', methods=["GET", "POST"])
def del_command(command_id):
	"""
	Функція видалення команди
	"""
	print('del')
	name = db.get_command_name(command_id)
	form = wtf.edit_command_form(name=name)
	form_dialog = wtf.del_dialog_form()
	print('form_dialog.submit.data  --  ', form_dialog.submit.data)

	if form_dialog.submit.data:
		print('Так')
	return redirect(url_for('settings_command', command_id=command_id))


if __name__ == '__main__':
	app.run(host=config.HOST, debug=config.DEBUG)

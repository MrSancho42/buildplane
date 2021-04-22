import sqlite3
from flask import Flask, render_template, g, redirect, url_for, request, flash, session
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
		print("pidar")
		render_template('add_command.html', form=form, user=session['user'])

	return render_template('add_command.html', form=form, user=session['user'])

@app.route('/home/task')
def home():
	"""
	Головна сторінка користувача
	"""
	return render_template('work_space.html', user=session['user'])


if __name__ == '__main__':
	app.run(host=config.HOST, debug=config.DEBUG)

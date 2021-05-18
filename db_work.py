from hashlib import sha256 as sha256
import sqlite3 as sqlite3
from datetime import datetime


"""
Робота із базою даних.
Через цей пакет необхідно вести запити до БД.
"""


class db_work():
	def __init__(self, cursor, user):
		self.__cur = cursor
		self.__cur.execute('PRAGMA foreign_keys = ON')
		self.__user = user


	@staticmethod
	def hash(value):
		"""
		Генератор хеш функцій.
		Може використовуватися як самостійний скрипт.

		Повертає захешоване заначення
		"""

		return sha256(str(value).encode('utf-8')).hexdigest()

	@staticmethod
	def to_timestamp(value):
		"""
		Приймає дату у форматі yyyy-mm-dd.
		
		Повертає timestamp
		"""

		return datetime.strptime(value, '%Y-%m-%d').strftime('%s')

	@staticmethod
	def from_timestamp(value):
		"""
		Приймає timestamp.

		Повертає дату у форматі dd.mm.yyyy
		"""

		return datetime.fromtimestamp(int(value)).strftime('%d.%m.%Y')


	def convert_date(self, col):
		"""
		Функція для конвертування дат завдань.

		Приймає цілу колонку.

		Повертає її змінений варіант. 
		"""

		col = [dict(task) for task in col]

		for task in col:
			if task['start_date']:
				task['start_date'] = self.from_timestamp(task['start_date'])

			if task['end_date']:
				task['end_date'] = self.from_timestamp(task['end_date'])

		return col


	def login(self, login, password):
		"""
		Функція для авторизації користувача.
		Перевіряє чи вписаний логін є у базі, та чи збігаються хеш функції
		паролів у базі та введеного.
		"""

		try:
			res = self.__cur.execute(f'SELECT user_id, password FROM users WHERE login = "{login}"').fetchone()
			if res['password'] == self.hash(password):
				return {'status': True, 'user': res['user_id']}

			return {'status': False, 'message': 'Неправильний пароль'}

		except:
			return {'status': False, 'message': 'Неправильний логін'}


	def registration(self, login, password, name):
		"""
		Функція реєстрації.
		Перевіряє чи введений пароль існує.
		Якщо ні то вводить інформацію користувача у базу.
		Повертає True

		Якщо із таким логіном користувач існує
		Повертає False
		"""

		if self.__cur.execute(f'SELECT * FROM users WHERE login = "{login}"').fetchone():
			return False

		self.__cur.execute('INSERT INTO users VALUES(NULL, ?, ?, ?, NULL)', (login, self.hash(password), name))
		return True


	#Користувач///////////////////////////////////////////////////////////////
	def get_user(self):
		"""
		Функція для отримання імені користувача.

		Повертає {user_id, name}
		"""

		return self.__cur.execute(f'''SELECT *
									FROM v_users
									WHERE user_id = "{self.__user}"''').fetchone()


	def get_user_login(self):
		"""
		Функція для отримання імені та логіну користувача.

		Повертає {user_id, name, login}
		"""

		return self.__cur.execute(f'''SELECT *
									FROM v_users_login
									WHERE user_id = "{self.__user}"''').fetchone()


	def get_personal_tasks(self):
		"""
		Функція що дістає завдання та колонки користувача.

		Повертає [{col_id, name, tasks: [{task_id, description, start_date, end_date, done, col_id}]}]
		або якщо колонок немає
		Повертає False
		"""

		cols = self.get_cols('user', self.__user)
		if not cols:
			return False

		for col in cols:
			res = self.__cur.execute(f'''SELECT *
										FROM v_personal_tasks
										WHERE col_id = {col['col_id']}''').fetchall()
			col['tasks'] = self.convert_date(res)

		return cols


	def set_personal_task_col(self, col, task):
		"""
		Функція що змінює колонку завдання.

		Якщо дані невірні, то нічого не відбувається.
		"""

		if int(col) in [i['col_id'] for i in self.get_cols('user', self.__user)]:
			self.__cur.execute(f'''UPDATE personal_tasks
								SET col_id = {col}
								WHERE task_id = {task} and user_id = {self.__user}''')


	def set_personal_task_status(self, status, task):
		self.__cur.execute(f'''UPDATE personal_tasks
								SET done = {int(status)}
								WHERE task_id = {task} and user_id = {self.__user}''')


	#Команди//////////////////////////////////////////////////////////////////
	def get_commands(self):
		"""
		Функція що дістає команди до яких належить користувач.

		Повертає {command_id, name, owner_id, user_id}
		"""

		res = self.__cur.execute(f'''SELECT * FROM v_command
								WHERE user_id = "{self.__user}"''').fetchall()
		if res:
			return [dict(i) for i in res]

		return False


	def get_command_info(self, command_id):
		"""
		Функція що дістає команду.

		Повертає {command_id, name}
		"""

		return self.__cur.execute(f'''SELECT command_id, name
									FROM v_command
									WHERE command_id = "{command_id}"''').fetchone()


	def get_users_in_command(self, command_id):
		'''
		Дістає користувачів у команді

		Повертає [(user_id, login)]
		'''

		users_id = self.__cur.execute(f'''SELECT user_id FROM commands_user
									WHERE command_id = {command_id}''').fetchall()
		users = []
		for i in users_id:
			login = self.__cur.execute(f'''SELECT login FROM users
									WHERE user_id = {i['user_id']}''').fetchone()
			users.append((i['user_id'], login['login']))
		return users


	def add_command(self, name, owner_id):
		"""
		Функція додання нової команди.

		Повертає True після виконання операції
		"""

		self.__cur.execute('INSERT INTO commands VALUES(NULL, ?, ?, NULL)', (name, owner_id))
		command_id = self.__cur.execute('SELECT last_insert_rowid() from commands').fetchone()[0]
		self.__cur.execute('INSERT INTO commands_user VALUES(?, ?)', (owner_id, command_id))
		return True


	def edit_command(self, command_id, name):
		"""
		Функція редагування команди

		Повертає True після виконання операції
		"""

		self.__cur.execute(f'UPDATE commands SET name = "{name}" WHERE command_id = {command_id}')
		return True


	def del_command(self, command_id):
		"""
		Функція видалення команди.

		"""

		# перебір груп
		groups = self.__cur.execute(f'''SELECT group_id FROM v_group
									WHERE command_id = {command_id}''').fetchall()

		if groups:
			for group in groups:
				self.del_group(group['group_id'])

		# перебір подій
		command_events = self.__cur.execute(f'''SELECT event_id FROM commands_event
									WHERE command_id = {command_id}''').fetchall()
		if command_events:
			for event in command_events:
				event = event['event_id']
				self.del_event(event)

		# перебір колонок
		cols_list = self.__cur.execute(f'''SELECT cols_order FROM v_command_cols
									WHERE command_id = {command_id}''').fetchall()
		if cols_list:
			for cols in cols_list:
				if cols['cols_order'] is not None:
					cols = cols['cols_order'].split(',')
					for col_id in cols:
						self.del_col('command', command_id, col_id)

		self.__cur.execute(f'DELETE FROM commands WHERE command_id = {command_id}')


	def get_command_tasks(self, command_id):
		"""
		Функція що дістає завдання та колонки команди.

		Повертає [{col_id, name, tasks: [{task_id, description, start_date,
										end_date, done, performer_id, col_id,
										command_id, name, owner_id, color,
										group_name}]}]
		або якщо колонок немає False
		"""

		cols = self.get_cols('command', command_id)
		if not cols:
			return False

		for col in cols:
			res = self.__cur.execute(f'''SELECT *
										FROM v_command_tasks
										WHERE col_id = {col['col_id']}''').fetchall()
			col['tasks'] = self.convert_date(res)

		return cols


	def get_command_tasks_group(self, command_id):
		cols = self.__cur.execute(f'''SELECT DISTINCT group_id, name, color
									FROM v_group
									WHERE command_id = "{command_id}"''')

		cols = [dict(col) for col in cols]

		for col in cols:
			res = self.__cur.execute(f'''SELECT *
										FROM v_command_tasks_group
										WHERE group_id = {col['group_id']}''').fetchall()
			col['tasks'] = self.convert_date(res)

		return cols


	def get_command_tasks_user(self, command_id):
		"""
		Функція що дістає завдання призначені користувачу та колонки команди.

		Повертає [{col_id, name, tasks: [{task_id, description, start_date,
										end_date, done, performer_id, col_id,
										command_id, name, owner_id, color,
										group_name}]}]
		або якщо колонок немає False
		"""

		cols = self.get_cols('command', command_id)
		if not cols:
			return False

		for col in cols:
			res = self.__cur.execute(f'''SELECT *
										FROM v_command_tasks
										WHERE col_id = {col['col_id']} and
										performer_id = {self.__user}''').fetchall()
			col['tasks'] = self.convert_date(res)

		return cols


	def set_command_task_col(self, col, task, command_id):
		"""
		Функція що змінює колонку завдання команди.

		Якщо дані невірні, то нічого не відбувається.
		"""

		if int(col) in [i['col_id'] for i in self.get_cols('command', command_id)]:
			self.__cur.execute(f'''UPDATE tasks
								SET col_id = {col}
								WHERE task_id = {task} and 
									(SELECT count("task_id")
									FROM "commands_task"
									WHERE "command_id" = {command_id} and "task_id" = {task}) = 1''')


	#Спільне для команд та груп///////////////////////////////////////////////
	def set_task_status(self, status, task, element, element_id):
		"""
		Функція що змінює статус виконання завдання.

		Якщо дані невірні, то нічого не відбувається.
		"""

		self.__cur.execute(f'''UPDATE tasks
								SET done = {int(status)}
								WHERE task_id = {task} and
									(SELECT count("task_id")
									FROM {element}s_task
									WHERE {element}_id = {element_id} and task_id = {task}) = 1''')


	def get_membership(self, element, element_id):
		"""
		Функція що перевіряє належність користувача до групи, або команди.

		Повертає True, або False
		"""

		res = self.__cur.execute(f'''SELECT count(*)
									FROM {element}s_user
									WHERE {element}_id = {element_id} and
										user_id = {self.__user}''').fetchone()

		return bool(res[0])


	def get_owner_rights(self, element_id, user_id, element):
		"""
		Перевіряє, чи є користувач власником об'єкту (команди чи групи).

		Якщо є - повертає True
		якщо нема
		повертає False
		"""

		result = self.__cur.execute(f'''SELECT owner_id FROM v_{element}
									WHERE {element}_id = {element_id}''').fetchone()
		if result['owner_id'] == user_id:
			return True
		else: return False


	def get_edit_group_rights(self, user_id, group_id):
		"""
		Перевіряє, чи має користувач права редагування групи

		Він має права на редагування, якщо є власником команди, якій належить
		група, або керівником цієї групи 
		Якщо є - повертає True
		якщо нема
		повертає False
		"""

		result1 = self.__cur.execute(f'''SELECT owner_id, command_id FROM v_group
									WHERE group_id = {group_id}''').fetchone()
		result2 = self.__cur.execute(f'''SELECT owner_id FROM v_command
									WHERE command_id = {result1['command_id']}''').fetchone()
		if result1['owner_id'] == user_id or result2['owner_id'] == user_id:
			return True
		return False


	#Групи////////////////////////////////////////////////////////////////////
	def get_groups(self, command_id):
		"""
		Функція що дістає групи команди до яких належить користувач.

		Повертає [{group_id, name, color, command_id, owner_id, blocked, user_id, command_owner_id}]
		"""

		res = self.__cur.execute(f'''SELECT *
									FROM v_group
									WHERE command_id = "{command_id}" and
										user_id = "{self.__user}"''')

		if res:
			return [dict(i) for i in res]

		return False


	def get_group_info(self, group_id):
		"""
		Функція що дістає групи команди до яких належить користувач.

		Повертає {group_id, name, command_id}
		"""

		return self.__cur.execute(f'''SELECT group_id, name, command_id
									FROM v_group
									WHERE group_id = "{group_id}"''').fetchone()


	def get_full_group_info(self, group_id):
		"""
		Функція, що дістає майже всі дані про групу.

		Повертає {group_id, name, color, command_id, owner_id, blocked}
		"""

		return self.__cur.execute(f'''SELECT group_id, name, color, command_id, owner_id, blocked
									FROM v_group
									WHERE group_id = "{group_id}"''').fetchone()


	def edit_group(self, group_id, name, owner_id, blocked, color):
		"""
		Функція редагування групи

		"""
		print("vars from db_work  --  ", group_id, name, owner_id, blocked, color)
		self.__cur.execute(f'''UPDATE groups SET name = "{name}", owner_id={owner_id},
							blocked={blocked}, color="{color}" WHERE group_id = {group_id}''')
		#рядок на додання нового власника до групи якщо його ще нема
	
	
	def del_group(self, group_id):
		"""
		Функція видалення групи
		"""

		# перебір подій
		group_events = self.__cur.execute(f'''SELECT event_id FROM groups_event
										WHERE group_id = {group_id}''').fetchall()
		if group_events:
			for event in group_events:
				event = event['event_id']
				self.del_event(event)

		# перебір колонок 
		cols_list = self.__cur.execute(f'''SELECT cols_order FROM v_group_cols
									WHERE group_id = {group_id}''').fetchall()
		if cols_list:
			for cols in cols_list:
				if cols['cols_order'] is not None:
					cols = cols['cols_order'].split(',')
					for col_id in cols:
						self.del_col('group', group_id, col_id)

		self.__cur.execute(f'DELETE FROM groups WHERE group_id = {group_id}')


	def get_group_tasks(self, group_id):
		"""
		Функція що дістає завдання та колонки команди.

		Повертає [{col_id, name, tasks: [{task_id, description, start_date, end_date, done, performer_id, col_id, group_id, name}]}]
		або якщо колонок немає False
		"""

		cols = self.get_cols('group', group_id)
		if not cols:
			return False

		for col in cols:
			res = self.__cur.execute(f'''SELECT *
										FROM v_group_tasks
										WHERE col_id = {col['col_id']}''').fetchall()
			col['tasks'] = self.convert_date(res)

		return cols


	def set_group_task_col(self, col, task, group_id):
		"""
		Функція що змінює колонку завдання команди.

		Якщо дані невірні, то нічого не відбувається.
		"""

		if int(col) in [i['col_id'] for i in self.get_cols('group', group_id)]:
			self.__cur.execute(f'''UPDATE tasks
								SET col_id = {col}
								WHERE task_id = {task} and 
									(SELECT count("task_id")
									FROM "groups_task"
									WHERE "group_id" = {group_id} and "task_id" = {task}) = 1''')


	def add_group(self, name, color, command_id, owner_id, creator_id, blocked):
		'''
		Функція додання нової групи

		Повертає id щойно створеної групи
		'''

		self.__cur.execute(f'''INSERT INTO groups VALUES(NULL, '{name}', '{color}', {command_id}, {owner_id}, {blocked}, NULL)''')
		group_id = self.__cur.execute("SELECT last_insert_rowid() from groups").fetchone()[0]
		self.__cur.execute(f'INSERT INTO groups_user VALUES({owner_id}, {group_id})')

		# перевірка, чи треба додати творця до групи (якщо не є власником)
		if owner_id != str(creator_id):
			self.__cur.execute(f'INSERT INTO groups_user VALUES({creator_id}, {group_id})')
		return group_id


	#Колонки//////////////////////////////////////////////////////////////////
	def get_cols(self, element, element_id):
		"""
		Функція що дістає колонки наданого елемента.

		Повертає [{col_id, name}],
		або якщо колонок немає
		Повертає False
		"""

		try:
			res = self.__cur.execute(f'''SELECT cols_order
										FROM v_{element}_cols
										WHERE {element}_id = {element_id}''').fetchone()
			res = res['cols_order'].split(',')

			cols_order = [self.__cur.execute(f'''SELECT * 
												FROM cols 
												WHERE col_id = {col}''')
												.fetchone() for col in res]

			cols_order = [dict(col) for col in cols_order]

			return cols_order

		except AttributeError:
			return False


	def del_col(self, element, element_id, col_id):
		"""
		Видаляє одну колонку

		Приймає ім'я та id елемента (команди, групи, користувача)
		та id колонки
		"""

		tasks = self.__cur.execute(f'''SELECT task_id FROM v_{element}_tasks
							WHERE {element}_id = {element_id}''').fetchall()
		if tasks:
			for task in tasks:
				task = task['task_id']
				self.__cur.execute(f'DELETE FROM tasks WHERE task_id = {task}')

		self.__cur.execute(f'DELETE FROM cols WHERE col_id = {col_id}')


	#Події////////////////////////////////////////////////////////////////////
	def del_event(self, event_id):
		"""
		Видаляє одну подію
		"""

		self.__cur.execute(f'DELETE FROM events WHERE event_id = {event_id}')


if __name__ == '__main__':
	print(db_work.hash(input('Введіть значення для хешування: ')))

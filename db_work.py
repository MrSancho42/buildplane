from hashlib import sha256 as sha256
import sqlite3 as sqlite3
import _pickle as cpickle


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


	def get_user(self):
		"""
		Функція для отримання імені користувача.

		Повертає {user_id, name}
		"""
		return self.__cur.execute(f'''SELECT *
									FROM v_users
									WHERE user_id = "{self.__user}"''').fetchone()


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
	

	def get_command_name(self, command_id):
		"""
		Функція що дістає команду.

		Повертає {command_id, name}
		"""

		return self.__cur.execute(f'''SELECT command_id, name
									FROM v_command
									WHERE command_id = "{command_id}"''').fetchone()


	def get_groups(self, command_id):
		"""
		Функція що дістає групи команди до яких належить користувач.

		Повертає [{group_id, name, color, command_id, manager_id, user_id, owner_id}]
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
			res = list(res['cols_order'].split(','))
			
			cols_order = [self.__cur.execute(f'''SELECT * 
												FROM cols 
												WHERE col_id = {col}''')
												.fetchone() for col in res]

			cols_order = [dict(col) for col in cols_order]

			return cols_order

		except AttributeError:
			return False


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
			col['tasks'] = res
			
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


	def get_command_tasks(self, command_id):
		"""
		Функція що дістає завдання та колонки команди.

		Повертає [{col_id, name, tasks: [{task_id, description, start_date, end_date, done, performer_id, col_id, command_id, name, owner_id}]}]
		або якщо колонок немає False
		"""

		cols = self.get_cols('command', command_id)
		if not cols:
			return False

		for col in cols:
			res = self.__cur.execute(f'''SELECT *
										FROM v_command_tasks
										WHERE col_id = {col['col_id']}''').fetchall()
			col['tasks'] = res
			
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
			col['tasks'] = res
			
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



if __name__ == '__main__':
	print(db_work.hash(input('Введіть значення для хешування: ')))

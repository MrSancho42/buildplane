from hashlib import sha256 as sha256
import sqlite3 as sqlite3
from datetime import datetime

from wtforms.widgets.core import Select


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
		if value:
			return value.strftime('%s')
		else:
			return 'NULL'


	@staticmethod
	def from_timestamp(value):
		"""
		Приймає timestamp.

		Повертає дату у форматі dd.mm.yyyy
		"""

		return datetime.fromtimestamp(int(value)).strftime('%d.%m.%Y')


	@staticmethod
	def from_timestamp_form(value):
		"""
		Приймає timestamp.

		Повертає дату у форматі yyyy-mm-dd hh:mm:ss
		"""
		if value: print(datetime.fromtimestamp(value))
		if value: return datetime.fromtimestamp(value)


	def convert_task_date(self, col):
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


	def event_order(self, events):
		"""
		Функція для сортування подій

		Приймає список подій

		Повертає список із п'ятьох списків які є проміжками часу. Також конвертує дати
		"""

		#переведення дати
		for event in events:
			if event['date']:
				event['date'] = self.from_timestamp(event['date'])

		now = datetime.fromtimestamp(datetime.now().timestamp())
		order = [[] for i in range(5)]

		for event in events:
			if event['date']:
				date = datetime.strptime(event['date'], '%d.%m.%Y')

				if now.strftime('%d.%m.%Y') == date.strftime('%d.%m.%Y'):
					order[2].append(event)

				elif now.strftime('%V') == date.strftime('%V') and now.strftime('%s') < date.strftime('%s'):
					order[3].append(event)

				elif now.strftime('%s') < date.strftime('%s'):
					order[4].append(event)

				else:
					order[1].append(event)

			else: order[0].append(event)

		return order


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


	def get_user_login(self, user_id=0):
		"""
		Функція для отримання імені та логіну користувача.

		Повертає {user_id, name, login}
		"""

		#якщо не передано user_id, то береться id користувача в сесії
		if user_id == 0:
			user_id = self.__user

		return self.__cur.execute(f'''SELECT *
									FROM v_users_login
									WHERE user_id = "{user_id}"''').fetchone()


	def check_user_login(self, login):
		"""
		Перевіряє, чи існує користувач з таким логіном

		Повертає id користувача якщо є
		Повертає False якщо нема
		"""
		
		res = self.__cur.execute(f'''SELECT *
									FROM v_users_login
									WHERE login = "{login}"''').fetchone()
		if res:
			return res[0]
		else:
			return False


	def get_personal_tasks(self):
		"""
		Функція що дістає завдання та колонки користувача.

		Повертає [{col_id, name, tasks: [{task_id, description, start_date,
										end_date, done}]}]
		або якщо колонок немає
		Повертає False
		"""

		cols = self.get_cols('user', self.__user)
		if not cols:
			return False

		for col in cols:
			res = self.__cur.execute(f'''SELECT task_id, description,
												start_date, end_date, done
										FROM v_personal_tasks
										WHERE col_id = {col['col_id']}''').fetchall()
			col['tasks'] = self.convert_task_date(res)

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
		"""
		Змінює сататус завдання, якщо користувач співпадає
		"""

		self.__cur.execute(f'''UPDATE personal_tasks
								SET done = {int(status)}
								WHERE task_id = {task} and user_id = {self.__user}''')


	def get_command_members(self, command_id):
		"""
		Дістає інформацію для формуання списку учасників команди

		Поверає [{user_id, name, login}, [{name, color}]]
		"""
		
		result = []
		users = self.__cur.execute(f'''SELECT user_id FROM v_command
										WHERE command_id = {command_id}''').fetchall()
		i = 0
		while i < len(users):
			result.append(self.__cur.execute(f'''SELECT * FROM v_users_login
										WHERE user_id = {users[i]['user_id']}''').fetchall())
			result[i].append(self.__cur.execute(f'''SELECT name, color FROM v_group_owner
										WHERE owner_id = {users[i]['user_id']} AND command_id = {command_id}''').fetchall())
			i += 1	

		return result


	def get_personal_event(self):
		"""
		Дістає події користувача

		Повертає {[{event_id, description, date, done}] * 5}
		"""

		res = self.__cur.execute(f'''SELECT event_id, description, date, done
									FROM v_personal_events
									WHERE user_id = {self.__user}''')

		return self.event_order([dict(item) for item in res])


	def set_personal_event_status(self, status, event):
		"""
		Змінює статус події
		"""

		self.__cur.execute(f'''UPDATE personal_events
								SET done = {int(status)}
								WHERE event_id = {event} and user_id = {self.__user}''')


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
										end_date, done, performer_id,
										name, color, group_name}]}]
		або якщо колонок немає False
		"""

		cols = self.get_cols('command', command_id)
		if not cols:
			return False

		for col in cols:
			res = self.__cur.execute(f'''SELECT task_id, description,
											start_date, end_date, done,
											performer_id, name,
											color, group_name
										FROM v_command_tasks
										WHERE col_id = {col['col_id']}''').fetchall()
			col['tasks'] = self.convert_task_date(res)

		return cols


	def get_command_tasks_group(self, command_id):
		"""
		Дістає завдання сортуючи за групами

		Повертає [{group_id, name, color, [{task_id, description, start_date,
										end_date, done, performer_id, name}]}]
		"""

		cols = self.__cur.execute(f'''SELECT DISTINCT group_id, name, color
									FROM v_group
									WHERE command_id = "{command_id}"''')

		cols = [dict(col) for col in cols]

		for col in cols:
			res = self.__cur.execute(f'''SELECT task_id, description,
											start_date, end_date, done,
											performer_id, name
										FROM v_command_tasks_group
										WHERE group_id = {col['group_id']}''').fetchall()
			col['tasks'] = self.convert_task_date(res)

		return cols


	def get_command_tasks_user(self, command_id):
		"""
		Функція що дістає завдання призначені користувачу та колонки команди.

		Повертає [{col_id, name, tasks: [{task_id, description, start_date,
										end_date, done, performer_id,
										color, group_name}]}]
		або якщо колонок немає False
		"""

		cols = self.get_cols('command', command_id)
		if not cols:
			return False

		for col in cols:
			res = self.__cur.execute(f'''SELECT task_id, description,
											start_date, end_date, done,
											performer_id,
											color, group_name
										FROM v_command_tasks
										WHERE col_id = {col['col_id']} and
										performer_id = {self.__user}''').fetchall()
			col['tasks'] = self.convert_task_date(res)

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


	def add_user_to_command(self, command_id):
		"""
		Додає користувача до команди
		"""

		self.__cur.execute(f'INSERT INTO commands_user VALUES({self.__user}, {command_id})')
		self.del_invitation(command_id)


	def del_user_from_command(self, user_id, command_id):
		"""
		Видаляє користувача і команди
		"""

		self.__cur.execute(f'''DELETE FROM commands_user
							WHERE command_id = {command_id} and user_id = {user_id}''')	


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


	def get_membership(self, element, element_id, user_id=0):
		"""
		Функція що перевіряє належність користувача до групи або команди.

		Повертає True, або False
		"""

		#якщо user_id не передано - береться id користувача із сесії
		if user_id == 0:
			user_id = self.__user

		res = self.__cur.execute(f'''SELECT count(*)
									FROM {element}s_user
									WHERE {element}_id = {element_id} and
										user_id = {user_id}''').fetchone()

		return bool(res[0])


	def get_owner_rights(self, element_id, element):
		"""
		Перевіряє, чи є користувач власником об'єкту (команди чи групи).

		Якщо є - повертає True
		якщо нема
		повертає False
		"""

		res = self.__cur.execute(f'''SELECT count(*)
									FROM v_{element}
									WHERE {element}_id = {element_id} and
										owner_id = {self.__user}''').fetchone()

		return bool(res[0])


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


	def get_events(self, element_id, element, all_event):
		"""
		Функція що дістає події
		Повертає {[{event_id, description, date, done}] * 5}
		"""

		if all_event:
			res = self.__cur.execute(f'''SELECT event_id, description, date,
												done
										FROM v_{element}_events
										WHERE {element}_id = {element_id}
										GROUP BY event_id
										ORDER BY date''')
		else:
			res = self.__cur.execute(f'''SELECT event_id, description, date,
												done
										FROM v_{element}_events
										WHERE {element}_id = {element_id}
											and user_id = {self.__user}''')
		
		return self.event_order([dict(item) for item in res])


	def set_event_status(self, status, event):
		"""
		Змінює статус події команди або групи
		"""

		self.__cur.execute(f'''UPDATE users_event
								SET done = {int(status)}
								WHERE event_id = {event} and user_id = {self.__user}''')


	#Групи////////////////////////////////////////////////////////////////////
	def get_groups(self, command_id):
		"""
		Функція що дістає групи команди до яких належить користувач.

		Повертає [{group_id, name, color, command_id, owner_id, blocked,
				user_id, command_owner_id}]
		"""

		res = self.__cur.execute(f'''SELECT *
									FROM v_group
									WHERE command_id = "{command_id}" and
										user_id = "{self.__user}"''')

		if res:
			return [dict(i) for i in res]

		return False


	def get_list_groups_owners(self, command_id, owner):
		'''
		Дістає список керівників груп в команді

		Повертає [(user_id, 'login - name')]
		'''

		res = [(owner['user_id'], owner['login'] + ' - ' + owner['name'])]
		users = self.__cur.execute(f'''SELECT owner_id FROM v_group_owner
										WHERE command_id={command_id} and
										owner_id != {owner['user_id']}
										GROUP BY owner_id''').fetchall()

		if users:
			for user in users:
				user_info = self.get_user_login(user['owner_id'])
				res.append((user['owner_id'], user_info['login'] + ' - ' + user_info['name']))
		return res


	def get_list_users_in_group(self, group_id):
		"""
		Дістає список коистувачів у групі

		Повертає [(user_id, 'login - name')]
		"""

		users = self.__cur.execute(f'''SELECT user_id FROM v_group
										WHERE group_id={group_id}''').fetchall()
		
		res = []
		if users:
			for user in users:
				user_info = self.get_user_login(user['user_id'])
				res.append((user['user_id'], user_info['login'] + ' - ' + user_info['name']))
		return res


	def get_group_info(self, group_id):
		"""
		Функція що дістає дані про групу

		Повертає {group_id, name, command_id, blocked}
		"""

		return self.__cur.execute(f'''SELECT group_id, name, command_id, blocked
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

		Повертає [{col_id, name, tasks: [{task_id, description, start_date,
										end_date, done, performer_id, name}]}]
		або якщо колонок немає False
		"""

		cols = self.get_cols('group', group_id)
		if not cols:
			return False

		for col in cols:
			res = self.__cur.execute(f'''SELECT task_id, description,
											start_date, end_date, done,
											performer_id, name
										FROM v_group_tasks
										WHERE col_id = {col['col_id']}''').fetchall()
			col['tasks'] = self.convert_task_date(res)

		return cols


	def get_group_tasks_user(self, group_id):
		"""
		Функція що дістає завдання користувача та колонки команди.

		Повертає [{col_id, name, tasks: [{task_id, description, start_date, end_date, done, performer_id}]}]
		або якщо колонок немає False
		"""

		cols = self.get_cols('group', group_id)
		if not cols:
			return False

		for col in cols:
			res = self.__cur.execute(f'''SELECT task_id, description,
											start_date, end_date, done,
											performer_id
										FROM v_group_tasks
										WHERE col_id = {col['col_id']} and
											performer_id = {self.__user}''').fetchall()
			col['tasks'] = self.convert_task_date(res)

		return cols


	def set_group_task_col(self, col, task, group_id):
		"""
		Функція що змінює колонку завдання групи.

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


	def del_col(self, element, col_id, element_id=False):
		"""
		Видаляє одну колонку

		Приймає ім'я та id елемента (команди, групи, користувача)
		та id колонки
		"""

		if not element_id:
			element_id = self.__user

		if element == 'user':
			tasks = self.__cur.execute(f'''SELECT task_id FROM v_personal_tasks
									WHERE col_id = {col_id}''').fetchall()
		else:
			tasks = self.__cur.execute(f'''SELECT task_id FROM v_{element}_tasks
									WHERE col_id = {col_id}''').fetchall()

		if tasks:
			for task in tasks:
				task = task['task_id']
				self.__cur.execute(f'DELETE FROM tasks WHERE task_id = {task}')

		cols_list = self.__cur.execute(f'''SELECT cols_order from v_{element}_cols
										WHERE {element}_id = {element_id}''').fetchone()[0]

		if str(col_id) + ',' in cols_list:
			cols_list = cols_list.replace(str(col_id) + ',', "")

		elif ',' + str(col_id) in cols_list:
			cols_list = cols_list.replace(',' + str(col_id), "")

		elif str(col_id) == cols_list:
			cols_list = ""

		if cols_list:
			self.__cur.execute(f'''UPDATE {element}s SET cols_order = '{cols_list}'
								WHERE {element}_id = {element_id}''')
		else:
			self.__cur.execute(f'''UPDATE {element}s SET cols_order = NULL
								WHERE {element}_id = {element_id}''')
		
		
		self.__cur.execute(f'DELETE FROM cols WHERE col_id = {col_id}')


	def add_col(self, element, col_name, element_id=False):
		"""
		Додає колонку
		"""

		if not element_id:
			element_id = self.__user

		cols_list = self.__cur.execute(f'''SELECT cols_order from v_{element}_cols
										WHERE {element}_id = {element_id}''').fetchone()[0]
		self.__cur.execute(f'''INSERT INTO cols VALUES(NULL, '{col_name}')''')
		col_id = self.__cur.execute('SELECT last_insert_rowid() from cols').fetchone()[0]
		if cols_list:
			cols_list = cols_list + ',' + str(col_id)
		else:
			cols_list = str(col_id)
		self.__cur.execute(f'''UPDATE {element}s SET cols_order = '{cols_list}'
								WHERE {element}_id = {element_id}''')


	def change_col_status(self, element, element_id, col_id, status):
		'''
		Змінює порядок колонки

		Якщо status == True то на одну позицію вправо
		Якщо status == False то на одну позицію вліво
		'''

		cols_list = self.__cur.execute(f'''SELECT cols_order from v_{element}_cols
										WHERE {element}_id = {element_id}''').fetchone()[0].split(',')

		replace = True
		i = 0
		while i < len(cols_list):
			if col_id == cols_list[i]:
				if i == 0:
					if status == True:
						replace = False
					else:
						cols_list = cols_list[1:]
						i += 1
				elif i == len(cols_list):
					if status == False:
						replace = False
					else:
						cols_list = cols_list[:i]
						i -= 1
				else:
					cols_list = cols_list[0:i] + cols_list[i+1:]
					if status == True:
						i -= 1
					else:
						i += 1
				break
			else: i += 1

		if replace:
			cols_list.insert(i, col_id)
		
		cols_list = ','.join(cols_list)
		self.__cur.execute(f'''UPDATE {element}s SET cols_order = '{cols_list}'
								WHERE {element}_id = {element_id}''')


	#Завдання/////////////////////////////////////////////////////////////////
	def add_personal_task(self, description, start_date, end_date, col_id):
		'''
		Додає подію користувача
		'''

		if start_date and end_date and start_date > end_date:
			return False


		self.__cur.execute(f'''INSERT INTO personal_tasks
							VALUES(NULL, '{description}',
								{db_work.to_timestamp(start_date)},
								{db_work.to_timestamp(end_date)}, 0,
								'{self.__user}', '{col_id}')''')
		
		return True


	def get_personal_task_info(self, task_id):
		'''
		Дістає інформацію про конкретне особисте завдання
		'''

		res = self.__cur.execute(f'''SELECT *
									FROM v_personal_tasks
									WHERE task_id = {task_id}
										and user_id = {self.__user}''').fetchone()
		
		if not res:
			return False

		res = dict(res)
		res['start_date'] = db_work.from_timestamp_form(res['start_date'])
		res['end_date'] = db_work.from_timestamp_form(res['end_date'])

		return res


	def edit_personal_task(self, task_id, description, start_date, end_date, col_id):
		'''
		Додає подію користувача
		'''

		if start_date and end_date and start_date > end_date:
			return False

		self.__cur.execute(f'''UPDATE  personal_tasks
								SET description = "{description}",
									start_date = {db_work.to_timestamp(start_date)},
									end_date = {db_work.to_timestamp(end_date)},
									col_id = {col_id}
								WHERE task_id = {task_id}''')
		
		return True


	def del_personal_task(self, task_id):
		self.__cur.execute(f'DELETE FROM personal_tasks WHERE task_id = {task_id}')


	#Події////////////////////////////////////////////////////////////////////
	def del_event(self, event_id):
		"""
		Видаляє одну подію
		"""

		print(event_id)
		self.__cur.execute(f'DELETE FROM users_event WHERE event_id = {event_id}')
		self.__cur.execute(f'DELETE FROM commands_event WHERE event_id = {event_id}')
		self.__cur.execute(f'DELETE FROM events WHERE event_id = {event_id}')


	def del_personal_event(self, event_id):
		"""
		Видаляє одну особисту подію
		"""

		self.__cur.execute(f'DELETE FROM personal_events WHERE event_id = {event_id}')


	def add_event(self, element, element_id, user_id, name, date):
		'''
		Додає подію для команди або групи
		'''

		if date:
			date = date.strftime("%s")
		else:
			date = 'NULL'
		
		self.__cur.execute(f'''INSERT INTO events VALUES(NULL, '{name}', {date})''')
		event_id = self.__cur.execute('SELECT last_insert_rowid() from events').fetchone()[0]
		self.__cur.execute(f'INSERT INTO {element}s_event VALUES({event_id}, {element_id})')
		self.__cur.execute(f'INSERT INTO users_event VALUES({event_id}, 0, {user_id})')


	def add_personal_event(self, name, date):
		'''
		Додає подію користувача
		'''

		if date:
			date = date.strftime("%s")
		else:
			date = 'NULL'
		self.__cur.execute(f'''INSERT INTO personal_events
							VALUES(NULL, '{name}', {date}, 0, {self.__user})''')


	def check_personal_event_owner(self, event_id):
		'''
		Визначає, чи є користувач власником особистої події
		'''

		res = self.__cur.execute(f'''SELECT user_id
									FROM v_personal_events
									WHERE event_id = "{event_id}"''').fetchone()[0]
		if res == self.__user:
			return True
		else:
			return False


	def get_personal_event_info(self, event_id):
		'''
		Дістає інформацію про конкретну особисту подію
		'''

		return self.__cur.execute(f'''SELECT description, date
									FROM v_personal_events
									WHERE event_id = {event_id}''').fetchone()



	def edit_personal_event(self, event_id, description, date):
		"""
		Функція редагування особистої події
		"""
		
		if date:
			self.__cur.execute(f'''UPDATE personal_events SET description = "{description}",
								date={date} WHERE event_id = {event_id}''')
		else:
			self.__cur.execute(f'''UPDATE personal_events SET description = "{description}",
								date=NULL WHERE event_id = {event_id}''')


	def get_event(self, event_id, element):
		'''
		Дістає інформацію про подію команди/групи

		Повертає {description, date, user_id}
		'''

		res = self.__cur.execute(f'''SELECT description, date, user_id
									FROM v_{element}_events
									WHERE event_id = {event_id}''').fetchone()
		return res

	
	def edit_event(self, event_id, description, user_id, date):
		'''
		Редагує подію команди/групи
		'''

		print('- - edit event - -')
		if description:
			print('e 1', description)
			self.__cur.execute(f'''UPDATE events SET description='{description}'
								WHERE event_id={event_id}''')
		if date:
			print('e 2', date)
			self.__cur.execute(f'''UPDATE events SET date={date}
								WHERE event_id={event_id}''')
		if date == None:
			print('e 3', date)
			self.__cur.execute(f'''UPDATE events SET date=NULL
								WHERE event_id={event_id}''')
		if user_id:
			print('e 4', user_id)
			self.__cur.execute(f'''UPDATE users_event SET user_id={user_id}
								WHERE event_id={event_id}''')


	def get_event_performers(self, event_id, element):
		'''
		Дістає виконавців події та дані про виконання

		Повертає [{user_id, login, name, done}]
		'''

		res = []
		users = self.__cur.execute(f'''SELECT user_id, done FROM v_{element}_events
										WHERE event_id = {event_id}''').fetchall()
		for user in users:
			info = self.get_user_login(user['user_id'])
			res.append([info['user_id'], info['login'], info['name'], user['done']])
		return res


	#Запрошення//////////////////////////////////////////////////////////////
	def check_send_nice_invitation(self, login, command_id):
		"""
		Крутезний метод надсилання запрошення

		Повертає {status, message}
		"""

		user_id = self.check_user_login(login)
		# перевірка чи існує користувач із таким логіном
		if user_id:
			
			# перевіряє, чи користувачеві вже надіслано запрошення
			if not self.__cur.execute(f'''SELECT * FROM invite
								WHERE user_id = "{user_id}" and command_id = "{command_id}"''').fetchall():
				
				#перевірка, чи такий користувач уже є в команді
				if self.get_membership('command', command_id, user_id):
					return {'status': False, 'message': 'Користувач уже є в цій команді'}

				else:
					# надсилання запрошення
					self.__cur.execute(f'INSERT INTO invite VALUES({user_id}, {command_id}, 1)')
					return {'status': True, 'message': 'Запрошення надіслано'}
			
			else:
				return {'status': False, 'message': 'Користувачеві вже надіслано запрошення'}

		else:
			return {'status': False, 'message': 'Користувача з таким логіном не існує'}


	def get_incoming_invitation(self):
		"""
		Перевіряє, чи є запрошення, які прийшли користувачеві

		Повертає [{command_id, name}] - якщо запрошення є
		False - якщо запрошень нема
		"""

		invitations = self.__cur.execute(f'''SELECT command_id FROM invite
								WHERE user_id = {self.__user} and status = 1''').fetchall()
		if invitations:
			result = []
			for invitation in invitations:
				result.append(self.get_command_info(invitation[0]))
			return result
		else: return False


	def get_sended_invitation(self, command_id, status):
		"""
		Перевіряє чи є відхилені (status=0) або надіслані (status=1) запрошення

		Повертає [{user_id, name, login}] - якщо запрошення є
		False - якщо запрошень нема
		"""

		invitations = self.__cur.execute(f'''SELECT user_id FROM invite
								WHERE command_id = {command_id} and status = {status}''').fetchall()
		if invitations:
			result = []
			for invitation in invitations:
				result.append(self.get_user_login(invitation[0]))
			return result
		else: return False


	def change_invitation_status(self, command_id, user_id=0):
		"""
		Змінює статус запрошення

		З 0 стає 1
		З 1 стає 0
		"""

		#якщо не передано user_id, то береться id користувача в сесії
		if user_id == 0:
			user_id = self.__user

		status = self.__cur.execute(f'''SELECT status FROM invite
								WHERE user_id = {user_id} and command_id = {command_id}''').fetchone()[0]

		if status == 1:
			self.__cur.execute(f'''UPDATE invite
								SET status = 0
								WHERE user_id = {user_id} and command_id = {command_id}''')
		else:
			self.__cur.execute(f'''UPDATE invite
								SET status = 1
								WHERE user_id = {user_id} and command_id = {command_id}''')


	def del_invitation(self, command_id, user_id=0):
		"""
		Видаляє запрошення
		"""

		#якщо не передано user_id, то береться id користувача в сесії
		if user_id == 0:
			user_id = self.__user

		self.__cur.execute(f'DELETE FROM invite WHERE user_id = {user_id} and command_id = {command_id}')


	def get_group_members(self, group_id):
		"""
		Дістає інформацію для формуання списку учасників групи

		Поверає [{user_id, name, login}]
		"""

		result = []
		users = self.__cur.execute(f'''SELECT user_id FROM v_group
										WHERE group_id = {group_id}''').fetchall()
		i = 0
		while i < len(users):
			result.append(self.__cur.execute(f'''SELECT * FROM v_users_login
										WHERE user_id = {users[i]['user_id']}''').fetchall())
			i += 1

		return result


	def add_user_to_group(self, group_id, user_id):
		"""
		Додає користувача до групи
		"""

		self.__cur.execute(f'INSERT INTO groups_user VALUES({user_id}, {group_id})')


	def del_user_from_group(self, user_id, group_id):
		"""
		Видаляє користувача і команди
		"""

		self.__cur.execute(f'''DELETE FROM groups_user
							WHERE group_id = {group_id} and user_id = {user_id}''')	


if __name__ == '__main__':
	print(db_work.hash(input('Введіть значення для хешування: ')))

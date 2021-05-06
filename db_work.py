from hashlib import sha256 as sha256
import sqlite3 as sqlite3
import _pickle as cpickle


"""
Робота із базою даних.
Через цей пакет необхідно вести запити до БД.
"""


class db_work():
	def __init__(self, cursor, session):
		self.__cur = cursor
		self.__cur.execute('PRAGMA foreign_keys = ON')
		self.__session = session
	

	@staticmethod	
	def hash(value):
		"""
		Генератор хеш функцій.
		Може використовуватися як самостійний скрипт.
		"""
		return sha256(str(value).encode('utf-8')).hexdigest()

	
	def login(self, login, password):
		try:
			res = self.__cur.execute(f'SELECT * FROM users WHERE login = "{login}"').fetchone()
			if res['password'] == self.hash(password):
				user = self.__cur.execute(f'''SELECT *
											FROM v_users
											WHERE user_id = "{res['user_id']}"''').fetchone()
				return {'status': True, 'user': dict(user)}
			
			return {'status': False, 'message': 'Неправильний пароль'}

		except:
			return {'status': False, 'message': 'Неправильний логін'}
	

	def registration(self, login, password, name):
		if self.__cur.execute(f'SELECT * FROM users WHERE login = "{login}"').fetchone():
			return False

		self.__cur.execute('INSERT INTO users VALUES(NULL, ?, ?, ?, NULL)', (login, self.hash(password), name))
		return True

	
	def get_commands(self):
		res = self.__cur.execute(f'''SELECT v_command.command_id, v_command.name, v_command.owner_id FROM v_command
								INNER JOIN commands_user
								ON commands_user.command_id = v_command.command_id
								WHERE commands_user.user_id = "{self.__session['user']['user_id']}"''').fetchall()
		return [dict(i) for i in res]
	

	def get_cols(self, element, element_id):
		try:
			res = self.__cur.execute(f'''SELECT cols_order
										FROM v_{element}_cols
										WHERE {element}_id = {element_id}''').fetchone()
			res = list(res['cols_order'].split(','))

			cols_order = []
			for col in res:
				cols_order.append(self.__cur.execute(f'SELECT * FROM cols WHERE col_id = {col}').fetchone())

			cols_order = [dict(col) for col in cols_order]

			return cols_order

		except AttributeError:
			return False


	def get_personal_tasks(self, cols):
		for col in cols:
			res = self.__cur.execute(f'''SELECT *
										FROM v_personal_tasks
										WHERE col_id = {col['col_id']}''').fetchall()
			col['tasks'] = res
			
		return cols

	def get_command_name(self, command_id):
		return self.__cur.execute(f"SELECT name FROM commands WHERE command_id = {command_id}").fetchone()[0]
			

	def add_command(self, name, owner_id):
		self.__cur.execute('INSERT INTO commands VALUES(NULL, ?, ?, NULL)', (name, owner_id))
		command_id = self.__cur.execute("SELECT last_insert_rowid() from commands").fetchone()[0]
		self.__cur.execute('INSERT INTO commands_user VALUES(?, ?)', (owner_id, command_id))
		return True
	
	def edit_command(self, command_id, name):
		self.__cur.execute(f"UPDATE commands SET name = '{name}' WHERE command_id = {command_id}")
		return True

	def del_command(self, comand_id):
		# перебір груп команди
		groups = self.__cur.execute(f'SELECT group_id FROM groups WHERE command_id = {comand_id}')
		if groups:
			print('groups')
			for group in groups:
				group_id = group['group_id']
				print('g', group_id)

				# перебір подій групи
				group_events = self.__cur.execute(f'SELECT event_id FROM groups_event WHERE group_id = {group_id}')
				if group_events:
					print('group events')
					for event in group_events:
						event_id = event['event_id']
						print('e', event)
				
				# перебір колонок групи
				list_group_cols = self.__cur.execute(f'SELECT cols_order FROM groups WHERE group_id = {group_id}')
				if list_group_cols:
					print('group cols')



		#for i in id_groups:
		#	print("hhh --- ", id_groups[i])
		#self.__cur.execute(f'DELETE FROM commands WHERE command_id = {comand_id}')
		#print("hi from db_work!")
		#groups = self.__cur.execute(f"SELECT group_id FROM commands WHERE command_id = {comand_id}").fetchall()
		#print(groups)
		#self.__cur.execute(f'DELETE FROM commands WHERE command_id = {comand_id}')
		#колонки!!!!
		#self.__cur.execute(f'DELETE FROM commands_event WHERE command_id = {comand_id}')
		#return True


if __name__ == '__main__':
	print(db_work.hash(input('Введіть значення для хешування: ')))

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


if __name__ == '__main__':
	print(db_work.hash(input('Введіть значення для хешування: ')))

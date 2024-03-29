import sqlite3
from os import remove
from os.path import exists, normcase, dirname, abspath
import config


"""
Скрипт для створення бази даних із схеми.
Шляхи беруться із файлу конфігурацій
"""

def get_path(f):
	"""
	Приймає шлях до файлу.
	Повертає повний нормалізований шлях до нього,
	відштовхуючись від місця запуску коду.
	"""
	return normcase(dirname(abspath(__file__)) + f)


def execute_script(path_to_file):
	"""
	Приймає SQL файл та виконує скрипт записаний
	у ньому.
	"""
	db = sqlite3.connect(get_path(config.DATABASE))

	with open(get_path(path_to_file), 'r') as file_sql:
		db.cursor().executescript(file_sql.read())

	db.commit()
	db.close()


if __name__ == '__main__':
	if exists(get_path(config.DATABASE)):
		if input('База даних уже існує. Створити нову? (т/Н) ') == 'т' or 'Т':
			remove(get_path(config.DATABASE)) #Перед створенням БД видаляє попередню
			execute_script(config.SHEMA)
	else:
		if input('Створити нову базу даних? (Т/н) ') != 'н' or 'Н':
			execute_script(config.SHEMA)

	if input('Імпортувати дані із "data.sql"? (Т/н) ') != 'н' or 'Н':
		execute_script(config.DB_DATA)

	if input('Створити представлення із "views.sql" (Т/н) ') != 'н' or 'Н':
		execute_script(config.VIEWS)

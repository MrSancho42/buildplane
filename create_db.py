import sqlite3
from os import path
from os.path import exists
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
	return path.normcase(path.dirname(path.abspath(__file__)) + f)

def create_db():
	db = sqlite3.connect(get_path(config.DATABASE))
	with open(get_path(config.SHEMA), 'r') as shema:
		db.cursor().executescript(shema.read())
	db.commit()
	db.close()


if __name__ == '__main__':
	if exists(config.DATABASE):
		if input('База даних уже існує. Створити нову? (т/Н) ') == 'т':
			create_db()
	else:
		if input('Створити нову базу даних? (Т/н) ') != 'н':
			create_db()

import sqlite3
from os.path import exists
import config


"""
Скрипт для створення бази даних із схеми.
Шляхи беруться із файлу конфігурацій
"""


def create_db():
	db = sqlite3.connect(config.DATABASE)
	with open(config.SHEMA, 'r') as shema:
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

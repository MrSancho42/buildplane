from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, InputRequired, Regexp


"""
Генератор форм.
Через нього варто генерувати усі форми.
По можливості)))
"""


class login_form(FlaskForm):
	login = StringField('Логін',
						validators=[Length(min=3, max=64,
										message='Логін повинен бути від 3 до 64 символів'),
						DataRequired(message='Заповніть це поле'),
						Regexp('[0-9a-zA-Z]', message='Заборонені символи')])
	psw = PasswordField('Пароль',
						validators=[Length(min=3, max=64,
										message='Пароль повинен бути від 3 до 64 символів'),
						DataRequired(message='Заповніть це поле')])
	remember = BooleanField('Запам\'ятати', default=False)
	submit = SubmitField('Увійти')


class reg_form(FlaskForm):
	login = StringField('Логін',
						validators=[Length(min=3, max=64,
										message='Логін повинен бути від 3 до 64 символів'),
						DataRequired(message='Заповніть це поле'),
						Regexp('[0-9a-zA-Z]', message='Заборонені символи')])
	name = StringField('Ім\'я', validators=[DataRequired(message='Заповніть це поле')])
	psw = PasswordField('Пароль',
						validators=[Length(min=3, max=64,
										message='Пароль повинен бути від 3 до 64 символів'),
						DataRequired(message='Заповніть це поле')])
	psw2 = PasswordField('Повторіть пароль',
						validators=[Length(min=3, max=64,
										message='Пароль повинен бути від 3 до 64 символів'),
						DataRequired(message='Заповніть це поле'),
						EqualTo('psw', message='Паролі не співпадають')])
	submit = SubmitField('Зареєструватися')

class add_command_form(FlaskForm):
	name = StringField("Назва команди", validators=[DataRequired(message='Заповніть це поле')])
	name1 = StringField("Фігнюшка для тесту 1", validators=[DataRequired(message='Заповніть це поле')])
	name2 = StringField("Фігнюшка для тесту 2", validators=[DataRequired(message='Заповніть це поле')])
	submit = SubmitField('Підтвердити')

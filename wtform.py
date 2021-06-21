from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField, RadioField
from wtforms.validators import DataRequired, Length, EqualTo, InputRequired, Regexp
from wtforms.widgets.html5 import ColorInput
from wtforms.widgets import TextArea
from wtforms.fields.html5 import DateField


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
	name = StringField("НАЗВА КОМАНДИ:", validators=[Length(min=1, max=30,
										message='Довжина назви повинна бути до 30 символів'),
						DataRequired(message='Заповніть це поле')])
	submit = SubmitField('Підтвердити')

class edit_command_form(FlaskForm):
	name = StringField('НАЗВА:', validators=[DataRequired(message='Заповніть це поле')])
	submit = SubmitField('Підтвердити')

class del_dialog_form(FlaskForm):
	submit = SubmitField('Так')

class add_group_form(FlaskForm):
	name = StringField("НАЗВА ГРУПИ:", validators=[Length(min=1, max=130,
										message='Довжина назви повинна бути до 130 символів'),
						DataRequired(message='Заповніть це поле')])	
	color = StringField('КОЛІР ГРУПИ:', widget=ColorInput())
	owner = SelectField('ВЛАСНИК ГРУПИ:')
	blocked = BooleanField('ЗАБОРОНИТИ РУХ ЗАВДАНЬ У КОЛОНКАХ:')
	submit = SubmitField('Підтвердити')

class edit_group_form(FlaskForm):
	name = StringField("НАЗВА ГРУПИ:", validators=[Length(min=1, max=130,
										message='Довжина назви повинна бути до 130 символів'),
						DataRequired(message='Заповніть це поле')])	
	color = StringField('КОЛІР ГРУПИ:', widget=ColorInput())
	owner = SelectField('ВЛАСНИК ГРУПИ:', choices=[], coerce=str, validate_choice=False)
	blocked = BooleanField('ЗАБОРОНИТИ РУХ ЗАВДАНЬ У КОЛОНКАХ:')
	submit = SubmitField('Підтвердити')

class add_command_member_form(FlaskForm):
	login = StringField("НАДІСЛАТИ ЗАПРОШЕННЯ:", render_kw={"placeholder": "логін користувача"},
						validators=[DataRequired(message='Заповніть це поле')])
	submit = SubmitField('Надіслати')

class add_group_member_form(FlaskForm):
	login = SelectField('ДОДАТИ КОРИСТУВАЧА:', choices=[], coerce=str, validate_choice=False)
	submit = SubmitField('Додати')

class add_new_col_form(FlaskForm):
	name = StringField('НАЗВА КОЛОНКИ:', validators=[DataRequired(message='Заповніть це поле')])
	submit = SubmitField('Додати')

class add_personal_event_form(FlaskForm):
	name = StringField('НАЗВА ПОДІЇ:', validators=[DataRequired(message='Заповніть це поле')])
	date = DateField('ДАТА НАСТАННЯ:')
	submit = SubmitField('Підтвердити')

class add_command_event_form(FlaskForm):
	name = StringField('НАЗВА ПОДІЇ:', validators=[DataRequired(message='Заповніть це поле')])
	user = RadioField("ПРИЗНАЧИТИ:", choices=[], coerce=str)
	date = DateField('ДАТА НАСТАННЯ:')
	submit = SubmitField('Підтвердити')

class edit_command_event_form(FlaskForm):
	name = StringField('НАЗВА ПОДІЇ:', validators=[DataRequired(message='Заповніть це поле')])
	user = RadioField("ПРИЗНАЧИТИ:", choices=[], coerce=str)
	date = DateField('ДАТА НАСТАННЯ:')
	submit = SubmitField('Підтвердити')

class add_personal_task_form(FlaskForm):
	description = StringField('Завдання:', validators=[DataRequired(message='Заповніть це поле')], widget=TextArea())
	start_date = DateField('Дата початку')
	end_date = DateField('Дата закінчення')
	cols = SelectField('Колонка', choices=[], coerce=str, validate_choice=False)
	submit = SubmitField('Підтвердити')	

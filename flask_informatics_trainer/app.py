from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Настройка базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Формы
class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

# Модель пользователя
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, default=0)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Теоретические материалы
theory_materials = {
    "Алгоритмы": [
        "Алгоритм - последовательность шагов для решения задачи",
        "Сложность алгоритма - оценка потребления ресурсов (времени и памяти)"
    ],
    "Программирование": [
        "ООП - программирование с использованием объектов (классы, наследование, полиморфизм)",
        "Функция - именованный блок кода для выполнения конкретной задачи"
    ],
    "Аппаратное обеспечение": [
        "ОЗУ - временная память для хранения данных во время работы компьютера",
        "SSD - твердотельный накопитель, быстрый тип хранилища данных"
    ]
}

# Генераторы вопросов
def generate_algorithm_questions():
    questions = [
        {
            'question': 'Что такое алгоритм?',
            'options': ['Последовательность действий', 'Язык программирования', 'Тип данных', 'Графический редактор'],
            'answer': 'Последовательность действий'
        },
        {
            'question': 'Какие из этих алгоритмов являются алгоритмами сортировки?',
            'options': ['Бинарный поиск', 'Пузырьковая сортировка', 'Поиск в глубину', 'Быстрая сортировка'],
            'answer': ['Пузырьковая сортировка', 'Быстрая сортировка']
        }
    ]
    random.shuffle(questions)
    return questions[:5]

def generate_programming_questions():
    questions = [
        {
            'question': 'Какой язык программирования является объектно-ориентированным?',
            'options': ['Python', 'HTML', 'CSS', 'SQL'],
            'answer': 'Python'
        },
        {
            'question': 'Что такое Git?',
            'options': ['Язык программирования', 'Система контроля версий', 'База данных', 'Фреймворк'],
            'answer': 'Система контроля версий'
        }
    ]
    random.shuffle(questions)
    return questions[:5]

def generate_hardware_questions():
    questions = [
        {
            'question': 'Что такое ОЗУ?',
            'options': ['Оперативное запоминающее устройство', 'Постоянное запнимающее устройство', 'Центральный процессор', 'Жёсткий диск'],
            'answer': 'Оперативное запоминающее устройство'
        },
        {
            'question': 'Что такое SSD?',
            'options': ['Тип процессора', 'Тип оперативной памяти', 'Тип жёсткого диска', 'Тип видеокарты'],
            'answer': 'Тип жёсткого диска'
        }
    ]
    random.shuffle(questions)
    return questions[:5]

# Разделы тестов
sections = {
    'algorithms': {
        'name': 'Алгоритмы',
        'generator': generate_algorithm_questions
    },
    'programming': {
        'name': 'Программирование',
        'generator': generate_programming_questions
    },
    'hardware': {
        'name': 'Аппаратное обеспечение',
        'generator': generate_hardware_questions
    }
}

# Маршруты
@app.route('/')
@login_required
def index():
    return render_template('menu.html',
                         sections=sections,
                         theory=theory_materials)


@app.route('/quiz/<section_name>', methods=['GET', 'POST'])
@login_required
def quiz(section_name):
    section = sections.get(section_name)
    if not section:
        flash('Раздел не найден.', 'danger')
        return redirect(url_for('index'))

    questions = section['generator']()

    if request.method == 'POST':
        score = 0
        for i, question in enumerate(questions):
            user_answers = request.form.getlist(f'question_{i}')
            correct_answers = question['answer'] if isinstance(question['answer'], list) else [question['answer']]

            if set(user_answers) == set(correct_answers):
                score += 1

        current_user.score += score
        db.session.commit()
        flash(f'Ваш результат: {score} из {len(questions)}', 'info')
        return redirect(url_for('index'))

    return render_template('quiz.html', section=section, questions=questions)


@app.route('/leaderboard')
@login_required
def leaderboard():
    users = User.query.order_by(User.score.desc()).all()
    return render_template('leaderboard.html', users=users)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            flash('Вы успешно вошли!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль.', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate  # Импортируем Flask-Migrate
from forms import RegistrationForm, LoginForm
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Настройка базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Инициализация Flask-Migrate

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Модель пользователя
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, default=0)  # Новое поле для рейтинга

# Генератор вопросов по алгоритмам
def generate_algorithm_questions():
    questions = [
        {
            'question': 'Что такое алгоритм?',
            'options': ['Последовательность действий', 'Язык программирования', 'Тип данных', 'Графический редактор'],
            'answer': 'Последовательность действий'
        },
        {
            'question': 'Какой из этих алгоритмов является алгоритмом сортировки?',
            'options': ['Бинарный поиск', 'Пузырьковая сортировка', 'Поиск в глубину', 'Хэширование'],
            'answer': 'Пузырьковая сортировка'
        },
        {
            'question': 'Что такое временная сложность алгоритма?',
            'options': ['Количество памяти, используемое алгоритмом', 'Время выполнения алгоритма', 'Количество операций в алгоритме', 'Скорость работы алгоритма'],
            'answer': 'Количество операций в алгоритме'
        },
        {
            'question': 'Что такое рекурсия?',
            'options': ['Метод оптимизации', 'Вызов функции самой себя', 'Тип данных', 'Структура данных'],
            'answer': 'Вызов функции самой себя'
        },
        {
            'question': 'Что такое "жадный алгоритм"?',
            'options': ['Алгоритм, который всегда выбирает локально оптимальное решение', 'Алгоритм, который работает медленно', 'Алгоритм, который использует много памяти', 'Алгоритм, который не всегда завершается'],
            'answer': 'Алгоритм, который всегда выбирает локально оптимальное решение'
        },
        {
            'question': 'Что такое бинарный поиск?',
            'options': ['Алгоритм поиска в отсортированном массиве', 'Алгоритм сортировки', 'Алгоритм для работы с графами', 'Алгоритм для работы с базами данных'],
            'answer': 'Алгоритм поиска в отсортированном массиве'
        }
    ]
    random.shuffle(questions)  # Перемешиваем вопросы
    return questions[:5]  # Возвращаем первые 5 уникальных вопросов

# Генератор вопросов по программированию
def generate_programming_questions():
    questions = [
        {
            'question': 'Какой язык программирования является объектно-ориентированным?',
            'options': ['Python', 'HTML', 'CSS', 'SQL'],
            'answer': 'Python'
        },
        {
            'question': 'Что такое ООП?',
            'options': ['Объектно-ориентированное программирование', 'Операционная система', 'Объектно-ориентированный процесс', 'Объектно-ориентированный проект'],
            'answer': 'Объектно-ориентированное программирование'
        },
        {
            'question': 'Что такое Git?',
            'options': ['Язык программирования', 'Система контроля версий', 'База данных', 'Фреймворк'],
            'answer': 'Система контроля версий'
        },
        {
            'question': 'Что такое "компиляция"?',
            'options': ['Процесс перевода исходного кода в машинный код', 'Процесс отладки программы', 'Процесс написания кода', 'Процесс тестирования программы'],
            'answer': 'Процесс перевода исходного кода в машинный код'
        },
        {
            'question': 'Что такое "функция" в программировании?',
            'options': ['Блок кода, который выполняет определённую задачу', 'Тип данных', 'Структура данных', 'Метод отладки'],
            'answer': 'Блок кода, который выполняет определённую задачу'
        },
        {
            'question': 'Что такое "цикл" в программировании?',
            'options': ['Конструкция для повторения блока кода', 'Тип данных', 'Метод сортировки', 'Структура данных'],
            'answer': 'Конструкция для повторения блока кода'
        }
    ]
    random.shuffle(questions)  # Перемешиваем вопросы
    return questions[:5]  # Возвращаем первые 5 уникальных вопросов

# Генератор вопросов по аппаратному обеспечению
def generate_hardware_questions():
    questions = [
        {
            'question': 'Что такое ОЗУ?',
            'options': ['Оперативное запоминающее устройство', 'Постоянное запоминающее устройство', 'Центральный процессор', 'Жёсткий диск'],
            'answer': 'Оперативное запоминающее устройство'
        },
        {
            'question': 'Что такое CPU?',
            'options': ['Центральный процессор', 'Оперативная память', 'Жёсткий диск', 'Видеокарта'],
            'answer': 'Центральный процессор'
        },
        {
            'question': 'Что такое SSD?',
            'options': ['Тип процессора', 'Тип оперативной памяти', 'Тип жёсткого диска', 'Тип видеокарты'],
            'answer': 'Тип жёсткого диска'
        },
        {
            'question': 'Что такое GPU?',
            'options': ['Графический процессор', 'Центральный процессор', 'Оперативная память', 'Жёсткий диск'],
            'answer': 'Графический процессор'
        },
        {
            'question': 'Что такое BIOS?',
            'options': ['Базовая система ввода-вывода', 'Тип оперативной памяти', 'Тип процессора', 'Тип жёсткого диска'],
            'answer': 'Базовая система ввода-вывода'
        },
        {
            'question': 'Что такое материнская плата?',
            'options': ['Основная плата компьютера, к которой подключаются все компоненты', 'Тип процессора', 'Тип оперативной памяти', 'Тип жёсткого диска'],
            'answer': 'Основная плата компьютера, к которой подключаются все компоненты'
        }
    ]
    random.shuffle(questions)  # Перемешиваем вопросы
    return questions[:5]  # Возвращаем первые 5 уникальных вопросов

# Генератор вопросов по сетям
def generate_networking_questions():
    questions = [
        {
            'question': 'Что такое IP-адрес?',
            'options': ['Уникальный идентификатор устройства в сети', 'Тип интернет-браузера', 'Протокол передачи данных', 'Тип кабеля'],
            'answer': 'Уникальный идентификатор устройства в сети'
        },
        {
            'question': 'Что такое DNS?',
            'options': ['Система доменных имён', 'Тип сети', 'Протокол передачи данных', 'Тип сервера'],
            'answer': 'Система доменных имён'
        },
        {
            'question': 'Что такое HTTP?',
            'options': ['Протокол передачи гипертекста', 'Язык программирования', 'Тип базы данных', 'Тип сети'],
            'answer': 'Протокол передачи гипертекста'
        },
        {
            'question': 'Что такое MAC-адрес?',
            'options': ['Уникальный идентификатор сетевого устройства', 'Тип IP-адреса', 'Протокол передачи данных', 'Тип кабеля'],
            'answer': 'Уникальный идентификатор сетевого устройства'
        },
        {
            'question': 'Что такое VPN?',
            'options': ['Виртуальная частная сеть', 'Тип интернет-браузера', 'Протокол передачи данных', 'Тип сервера'],
            'answer': 'Виртуальная частная сеть'
        },
        {
            'question': 'Что такое TCP/IP?',
            'options': ['Набор протоколов для передачи данных в сети', 'Тип интернет-браузера', 'Тип кабеля', 'Тип сервера'],
            'answer': 'Набор протоколов для передачи данных в сети'
        }
    ]
    random.shuffle(questions)  # Перемешиваем вопросы
    return questions[:5]  # Возвращаем первые 5 уникальных вопросов

# Генератор вопросов по базам данных
def generate_database_questions():
    questions = [
        {
            'question': 'Что такое SQL?',
            'options': ['Язык программирования', 'Язык запросов к базам данных', 'Тип базы данных', 'Тип сети'],
            'answer': 'Язык запросов к базам данных'
        },
        {
            'question': 'Что такое PRIMARY KEY в базе данных?',
            'options': ['Уникальный идентификатор записи', 'Тип данных', 'Тип индекса', 'Тип таблицы'],
            'answer': 'Уникальный идентификатор записи'
        },
        {
            'question': 'Что такое JOIN в SQL?',
            'options': ['Операция объединения таблиц', 'Тип данных', 'Тип индекса', 'Тип запроса'],
            'answer': 'Операция объединения таблиц'
        },
        {
            'question': 'Что такое "нормализация базы данных"?',
            'options': ['Процесс организации данных для уменьшения избыточности', 'Тип запроса', 'Тип индекса', 'Тип таблицы'],
            'answer': 'Процесс организации данных для уменьшения избыточности'
        },
        {
            'question': 'Что такое "индекс" в базе данных?',
            'options': ['Структура для ускорения поиска данных', 'Тип запроса', 'Тип таблицы', 'Тип данных'],
            'answer': 'Структура для ускорения поиска данных'
        },
        {
            'question': 'Что такое "транзакция" в базе данных?',
            'options': ['Набор операций, выполняемых как единое целое', 'Тип запроса', 'Тип индекса', 'Тип таблицы'],
            'answer': 'Набор операций, выполняемых как единое целое'
        }
    ]
    random.shuffle(questions)  # Перемешиваем вопросы
    return questions[:5]  # Возвращаем первые 5 уникальных вопросов

# Разделы с заданиями
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
    },
    'networking': {
        'name': 'Сети',
        'generator': generate_networking_questions
    },
    'databases': {
        'name': 'Базы данных',
        'generator': generate_database_questions
    }
}

@app.route('/')
@login_required
def index():
    return render_template('menu.html', sections=sections)

@app.route('/quiz/<section_name>', methods=['GET', 'POST'])
@login_required
def quiz(section_name):
    section = sections.get(section_name)
    if not section:
        flash('Раздел не найден.', 'danger')
        return redirect(url_for('index'))

    # Генерация 5 уникальных вопросов для теста
    questions = section['generator']()

    if request.method == 'POST':
        score = 0
        for i, question in enumerate(questions):
            user_answer = request.form.get(f'question_{i}')
            if user_answer == question['answer']:
                score += 1
        # Обновляем рейтинг пользователя
        current_user.score += score
        db.session.commit()
        flash(f'Ваш результат: {score} из {len(questions)}', 'info')
        return redirect(url_for('index'))

    return render_template('quiz.html', section=section, questions=questions)

@app.route('/leaderboard')
@login_required
def leaderboard():
    # Получаем всех пользователей, отсортированных по рейтингу (по убыванию)
    users = User.query.order_by(User.score.desc()).all()
    return render_template('leaderboard.html', users=users)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data)  # В реальном приложении хэшируйте пароль!
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
        if user and user.password == form.password.data:  # В реальном приложении используйте проверку хэша!
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
        db.create_all()  # Создаёт таблицы в базе данных
    app.run(debug=True)
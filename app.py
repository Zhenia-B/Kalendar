from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///schedule.db'
db = SQLAlchemy(app)

# Модель для зберігання дій
class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    action = db.Column(db.String(200), nullable=False)

# Функція для створення таблиць в базі даних
def create_tables():
    with app.app_context():
        db.create_all()

# Створення таблиць у базі даних
create_tables()

@app.route('/')
def index():
    # Отримання розкладу для всіх днів
    schedule = {}
    for day_name in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        schedule[day_name] = Action.query.filter_by(day=day_name).all()
    return render_template('index.html', schedule=schedule)

@app.route('/day/<day_name>', methods=['GET', 'POST'])
def show_day(day_name):
    if request.method == 'POST':
        time = request.form['time']
        action_text = request.form['action']
        
        # Перевірка формату часу за допомогою регулярних виразів
        if not re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', time):
            return "Неправильний формат часу. Введіть час у форматі години:хвилини."
        
        # Розділення годин та хвилин
        hour, minute = map(int, time.split(':'))
        
        # Перевірка на діапазон годин
        if hour < 0 or hour > 23:
            return "Неправильний формат годин. Години мають бути від 00 до 23."
        
        # Перевірка на діапазон хвилин
        if minute < 0 or minute > 59:
            return "Неправильний формат хвилин. Хвилини мають бути від 00 до 59."
        
        # Додавання нової дії, якщо час відповідає формату
        new_action = Action(day=day_name, time=time, action=action_text)
        db.session.add(new_action)
        db.session.commit()
        
        return redirect(url_for('show_day', day_name=day_name))
    
    schedule = Action.query.filter_by(day=day_name).all()
    return render_template('monday.html', schedule=schedule)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_action(id):
    action_to_delete = Action.query.get_or_404(id)
    db.session.delete(action_to_delete)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_action(id):
    action_to_edit = Action.query.get_or_404(id)
    if request.method == 'POST':
        action_to_edit.time = request.form['time']
        action_to_edit.action = request.form['action']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', action=action_to_edit)

@app.route('/return_home')
def return_home():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

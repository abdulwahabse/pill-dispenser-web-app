from datetime import datetime
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dfewfew123213rwdsgert34tgfd1234grgsf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Pill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(20), nullable=False)
    schedules = db.relationship('Schedule', backref='pill', lazy=True)

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(5), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    pill_id = db.Column(db.Integer, db.ForeignKey('pill.id'), nullable=False)
    logs = db.relationship('Log', backref='schedule', lazy=True)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_taken = db.Column(db.Boolean, default=False)
    date_time = db.Column(db.DateTime, default=datetime.utcnow)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/add_schedule', methods=['GET', 'POST'])
def add_schedule():
    if request.method == 'POST':
        day = request.form['day']
        time = request.form['time']
        quantity = request.form['quantity']
        pill_id = request.form['pill_id']
        new_schedule = Schedule(day=day, time=time, quantity=quantity, pill_id=pill_id)
        db.session.add(new_schedule)
        db.session.commit()
        return redirect('/')
    pills = Pill.query.all()
    return render_template('add_schedule.html', pills=pills)

@app.route('/delete_schedule/<int:schedule_id>', methods=['POST'])
def delete_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    db.session.delete(schedule)
    db.session.commit()
    return redirect('/')

@app.route('/edit_schedule/<int:schedule_id>', methods=['GET', 'POST'])
def edit_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    if request.method == 'POST':
        schedule.day = request.form['day']
        schedule.time = request.form['time']
        schedule.quantity = request.form['quantity']
        schedule.pill_id = request.form['pill_id']
        db.session.commit()
        return redirect('/')
    pills = Pill.query.all()
    return render_template('edit_schedule.html', schedule=schedule, pills=pills)

@app.route('/add_pill', methods=['GET', 'POST'])
def add_pill():
    if request.method == 'POST':
        name = request.form['name']
        dosage = request.form['dosage']
        new_pill = Pill(name=name, dosage=dosage)
        db.session.add(new_pill)
        db.session.commit()
        return redirect('/')
    return render_template('add_pill.html')

@app.route('/delete_pill/<int:pill_id>', methods=['POST'])
def delete_pill(pill_id):
    pill = Pill.query.get_or_404(pill_id)
    db.session.delete(pill)
    db.session.commit()
    return redirect('/')

@app.route('/edit_pill/<int:pill_id>', methods=['GET', 'POST'])
def edit_pill(pill_id):
    pill = Pill.query.get_or_404(pill_id)
    if request.method == 'POST':
        pill.name = request.form['name']
        pill.dosage = request.form['dosage']
        db.session.commit()
        return redirect('/')
    return render_template('edit_pill.html', pill=pill)

@app.route('/')
@app.route('/index.html')
def index():
    schedules = Schedule.query.all()
    pills = Pill.query.all()
    return render_template('index.html', schedules=schedules, pills=pills)

if __name__ == '__main__':
    app.run(debug=True)
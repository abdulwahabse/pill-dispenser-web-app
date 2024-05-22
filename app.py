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
    tank = db.Column(db.String(1), nullable=False, default='a')
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
    # intake_status = ('taken', 'missed')
    intake_status = db.Column(db.String(6), nullable=False)
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
        tank = request.form['tank']
        new_pill = Pill(name=name, dosage=dosage, tank=tank)
        db.session.add(new_pill)
        db.session.commit()
        return redirect('/')
    
    taken_tank_a = False
    taken_tank_b = False
    pills = Pill.query.all()
    if len(pills) == 1:
        tank = pills[0].tank
        if tank == 'a':
            taken_tank_a = True
        else:
            taken_tank_b = True
    return render_template('add_pill.html', taken_tank_a=taken_tank_a, taken_tank_b=taken_tank_b)

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
        pill.tank = request.form['tank']
        db.session.commit()
        return redirect('/')
    return render_template('edit_pill.html', pill=pill)

@app.route('/')
@app.route('/index.html')
def index():
    schedules = Schedule.query.all()
    pills = Pill.query.all()
    logs = Log.query.all()
    disable_add_schedule = False
    are_two_pills = False
    if len(pills) == 2:
        are_two_pills = True
    if len(pills) == 0:
        disable_add_schedule = True
    return render_template('index.html', schedules=schedules, pills=pills, logs=logs, disable_add_schedule=disable_add_schedule, are_two_pills=are_two_pills)

@app.route('/api/now')
def now():
    return {
        'status': 'success',
        'day': datetime.now().strftime('%A'), 
        'time': datetime.now().strftime('%H:%M:%S')
    }

@app.route('/api/server_status')
def server_status():
    return {
        'status': 'success',
        'server_status': 'running'
    }

@app.route('/api/logs', methods=['POST'])
def logs():
    data = request.get_json()
    if 'intake_status' not in data or 'schedule_id' not in data:
        return {'status': 'error', 'message': 'missing status or schedule_id'}, 400
    # if schedule_id is not found in the database then return HTTP code 404
    if not Schedule.query.get(data['schedule_id']):
        return {'status': 'error', 'message': 'schedule_id not found'}, 404
    new_log = Log(intake_status=data['intake_status'], schedule_id=data['schedule_id'])
    db.session.add(new_log)
    db.session.commit()
    return {'status': 'success', 'message': 'log added successfully'}

@app.route('/api/upcoming_pills')
def upcoming_pills():
    day = datetime.now().strftime('%A')
    time = datetime.now().strftime('%H:%M')
    schedules = Schedule.query.all()
    upcoming_pills = []
    for schedule in schedules:
        if schedule.day == day and schedule.time > time:
            upcoming_pills.append({
                'schedule_id': schedule.id,
                'pill_name': schedule.pill.name,
                'tank': schedule.pill.tank,
                'quantity': schedule.quantity,
                'time': schedule.time
            })
    upcoming_pills = sorted(upcoming_pills, key=lambda x: x['time'])
    return {
        'status': 'success',
        'upcoming_pills': upcoming_pills[:2]
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0')
    # app.run(debug=True)
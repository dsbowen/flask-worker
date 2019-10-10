"""Example app"""

from factory import create_app, db, socketio
from models import Employer, Worker

app = create_app()

@app.before_first_request
def before_first_request():
    db.create_all()
    employer = Employer.query.first()
    if employer is None:
        employer = Employer()
        db.session.add(employer)
    db.session.commit()

@app.route('/')
def index():
    employer = Employer.query.first()
    return employer.worker()

@app.route('/callback_route')
def callback_route():
    return 'Callback successful'

if __name__ == '__main__':
    socketio.run(app)

@app.shell_context_processor
def make_shell_context():
    db.create_all()
    employer = Employer.query.first()
    if employer is None:
        employer = Employer()
        db.session.add(employer)
        db.session.commit()
    return globals()
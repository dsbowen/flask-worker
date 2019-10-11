"""Example app"""

from factory import create_app, db, socketio
from models import Router, Employer, Worker

app = create_app()

@app.before_first_request
def before_first_request():
    db.create_all()
    employer = Employer.query.first()
    if employer is None:
        employer = Employer()
        db.session.add(employer)
    router = Router.query.first()
    if router is None:
        router = Router()
        db.session.add(router)
    db.session.commit()

@app.route('/')
def index():
    employer = Employer.query.first()
    worker = employer.worker
    db.session.commit()
    return worker()

@app.route('/callback_route')
def callback_route():
    db.session.commit()
    return 'Callback'

@app.route('/test')
def test():
    employer = Employer.query.first()
    worker = employer.worker
    if worker.ready_to_work or worker.job_in_progress:
        return worker()
    worker.reset()
    db.session.commit()
    return 'Test complete'

@app.route('/my-route')
def my_route():
    return Router.query.first().route()

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
"""Example app"""

from factory import create_app, db, socketio
from models import Employer, Router4_1, Router4_2, get_model

app = create_app()

@app.before_first_request
def before_first_request():
    db.create_all()

@app.route('/example1')
def example1():
    print('Request for /example1')
    employer = get_model(Employer, 'employer1')
    worker = employer.worker
    db.session.commit()
    if not worker.job_finished:
        return worker()
    return 'Example 1 finished'

@app.route('/example2')
def example2():
    print('Request for /example2')
    employer = get_model(Employer, 'employer2')
    worker = employer.worker
    if not worker.job_finished:
        db.session.commit()
        return worker()
    worker.reset()
    db.session.commit()
    return 'Example 2 finished'

@app.route('/example3')
def example3():
    print('Request for /example3')
    employer = get_model(Employer, 'employer3')
    worker = employer.worker
    worker.callback = 'callback_route'
    db.session.commit()
    return worker()

@app.route('/callback_route')
def callback_route():
    print('Request for /callback_route')
    employer = get_model(Employer, 'employer3')
    worker = employer.worker
    if not worker.job_finished:
        return worker()
    return 'Example 3 finished'

@app.route('/example4-no-router')
def example4_no_router():
    print('Request for /example4-no-router')
    return func1('hello world')

def func1(hello_world):
    print(hello_world)
    return func2('hello moon')

def func2(hello_moon):
    print(hello_moon)
    employer = get_model(Employer, 'employer4-no-router')
    employer.complex_task(seconds=5)
    return func3('hello star')

def func3(hello_star):
    print(hello_star)
    db.session.commit()
    return 'Example 4 (no router) finished'

@app.route('/example4.1')
def example4_1():
    print('Request for /example4.1')
    router = get_model(Router4_1, 'router4.1')
    return router.route()

@app.route('/example4.2')
def example4_2():
    print('Requestion for /example4.2')
    router = get_model(Router4_2, 'router4.2')
    return router.route()

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
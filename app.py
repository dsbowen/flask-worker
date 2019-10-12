"""Example app"""

from factory import create_app, db, socketio
from models import Employer, Router4, Router5, get_model

app = create_app()

@app.before_first_request
def before_first_request():
    db.create_all()

@app.route('/example1-no-worker')
def example1_no_worker():
    print('Request for /example1-no-worker')
    employer = get_model(Employer, 'employer1-no-worker')
    employer.complex_task(seconds=5)
    return 'Example 1 (no worker) finished'

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
    worker.reset()
    db.session.commit()
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

@app.route('/example4')
def example4():
    print('Request for /example4')
    router = get_model(Router4, 'router4')
    return router.route()

@app.route('/example5')
def example5():
    print('Request for /example5')
    router = get_model(Router5, 'router5')
    return router.route()

if __name__ == '__main__':
    socketio.run(app)
"""Example app

This file creates a Flask application and defines view functions with and 
without Workers and Routers.
"""

from factory import create_app, db, socketio
from models import Worker, get_model

app = create_app()

# create database before first app request
@app.before_first_request
def before_first_request():
    db.create_all()

# no worker
def complex_task(seconds):
    import time
    print('Complex task started')
    for i in range(seconds):
        print('Progress: {}%'.format(100.0*i/seconds))
        time.sleep(1)
    print('Progress: 100.0%')
    print('Complex task finished')
    return 'Hello, World!'

@app.route('/no-worker')
def no_worker():
    return complex_task(seconds=5)

# with worker
@app.route('/')
@app.route('/index')
def index():
    worker = get_model(Worker, 'index')
    return worker.result if worker.job_finished else worker()

# reset
@app.route('/reset')
def with_reset():
    worker = get_model(Worker, 'reset')
    if not worker.job_finished:
        return worker()
    worker.reset()
    db.session.commit()
    return worker.result

# callback
@app.route('/callback')
def with_callback():
    worker = get_model(Worker, 'callback')
    worker.callback = 'callback_route'
    if worker.job_finished:
        worker.reset()
    return worker()

@app.route('/callback_route')
def callback_route():
    worker = get_model(Worker, 'callback')
    return worker.result if worker.job_finished else worker()

# no router
@app.route('/no-router')
def no_router():
    return func1('hello world')

def func1(hello_world):
    print(hello_world)
    return func2('hello moon')

def func2(hello_moon):
    print(hello_moon)
    worker = get_model(Worker, 'no_router')
    return func3(worker.result) if worker.job_finished else worker()

def func3(hello_star):
    print(hello_star)
    db.session.commit()
    return 'Function calls finished.'

# routing
from models import Router

@app.route('/router')
def routing():
    return get_model(Router, 'routing')()

if __name__ == '__main__':
    socketio.run(app, debug=True)
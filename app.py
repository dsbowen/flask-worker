"""Example app

This file creates a Flask application and defines view functions with and 
without Workers and Routers.
"""

from factory import create_app, db, socketio
from models import Employer, get_model

app = create_app()

@app.before_first_request
def before_first_request():
    db.create_all()

"""No worker

This view function illustrates the basic problem Flask-Worker solves; a model 
(the employer) must run a long, complex task before the next page loads.

What we want is for the complex task to run once, and for the view function 
to return a loading page while the complex task is running. While the task is 
running, additional requests to this route should not cause the complex task 
to run multiple times.

However, in this example, there is no loading page, and every request to the 
route queues up another run of the complex task.
"""
@app.route('/no-worker')
def no_worker():
    print('Request for /no-worker')
    employer = get_model(Employer, 'no-worker')
    employer.complex_task(seconds=5)
    return 'Complex task finished.'

# basic
@app.route('/')
@app.route('/index')
def basic():
    print('Request for /index')
    employer = get_model(Employer, 'index')
    worker = employer.worker
    if not worker.job_finished:
        return worker()
    return 'Complex task finished.'

# reset
@app.route('/reset')
def with_reset():
    print('Request for /reset')
    employer = get_model(Employer, 'reset')
    worker = employer.worker
    if not worker.job_finished:
        return worker()
    worker.reset()
    db.session.commit()
    return 'Complex task finished. Reload the page to execute the task again.'

# callback
@app.route('/callback')
def with_callback():
    print('Request for /callback')
    employer = get_model(Employer, 'callback')
    worker = employer.worker
    worker.callback = 'callback_route'
    return worker()

@app.route('/callback_route')
def callback_route():
    print('Request for /callback_route')
    employer = get_model(Employer, 'callback')
    worker = employer.worker
    if not worker.job_finished:
        return worker()
    worker.reset()
    db.session.commit()
    return 'This is the callback route.'

# no router
@app.route('/no-router')
def no_router():
    print('Request for /no-router')
    return func1('hello world')

def func1(hello_world):
    print(hello_world)
    return func2('hello moon')

def func2(hello_moon):
    print(hello_moon)
    employer = get_model(Employer, 'no-router')
    employer.complex_task(seconds=5)
    return func3('hello star')

def func3(hello_star):
    print(hello_star)
    db.session.commit()
    return 'Function calls finished.'

# basic routing
from router_models import Router

@app.route('/router')
def basic_routing():
    print('Request for /router')
    router = get_model(Router, 'router')
    return router.route()

# resetting a router
from router_models import RouterWithReset

@app.route('/router-reset')
def routing_with_reset():
    print('Request for /router-reset')
    router = get_model(RouterWithReset, 'router_reset')
    return router.route()

if __name__ == '__main__':
    socketio.run(app, debug=True)
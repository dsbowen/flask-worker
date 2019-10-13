"""Example app

This file creates a Flask application and defines view functions with and 
without Workers and Routers.
"""

from factory import create_app, db, socketio
from models import Employer, get_model
from router_models import Router4, Router5

app = create_app()

@app.before_first_request
def before_first_request():
    db.create_all()

"""Example 1 (no worker)

This view function illustrates the basic problem Flask-Worker solves; a model 
(the employer) must run a long, complex task before the next page loads.

What we want is for the complex task to run once, and for the view function 
to return a loading page while the complex task is running. While the task is 
running, additional requests to the view function should not cause the 
complex task to be run multiple times.

However, in this example, there is no loading page, and every request to the 
route queues up another run of the complex task.
"""
@app.route('/example1-no-worker')
def example1_no_worker():
    print('Request for /example1-no-worker')
    employer = get_model(Employer, 'employer1-no-worker')
    employer.complex_task(seconds=5)
    return 'Example 1 (no worker) finished'

"""Example 1

In this view function, the employer uses its worker to execute its complex 
task. 

The worker only sends the employer's complex task to the Redis Queue once, 
regardless of how many times the client requests this route. Until the worker 
finishes its job, it returns a loading page. The result is cached once the 
worker finishes its job.
"""
@app.route('/example1')
def example1():
    print('Request for /example1')
    employer = get_model(Employer, 'employer1')
    worker = employer.worker
    if not worker.job_finished:
        return worker()
    return 'Example 1 finished'

"""Example 2

Example 2 is similar to Example 1. However, once the worker finishes its job, 
it is reset. If the client requests this route after the job has finished, 
the worker will queue up a new job.
"""
@app.route('/example2')
def example2():
    print('Request for /example2')
    employer = get_model(Employer, 'employer2')
    worker = employer.worker
    if not worker.job_finished:
        return worker()
    worker.reset()
    db.session.commit()
    return 'Example 2 finished'

"""Example 3

Example 3 demonstrates the worker's callback function. Once the worker has 
finished its job, it redirects the client to the callback route.

Note that the callback route will return the same loading page until the 
worker has finished its job.
"""
@app.route('/example3')
def example3():
    print('Request for /example3')
    employer = get_model(Employer, 'employer3')
    worker = employer.worker
    worker.callback = 'callback_route'
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

"""Example 4

This view function illustrates the problem that Routers solve; a request 
initiates a series of function calls. Among these functions is the employer's 
complex task.

What we want is to 'pause' the series of function calls when the complex task 
is executed. The view function should return a loading page while the complex 
task is running. Once the worker finishes its complex task, the view function 
should pick up where it left off with respect to the series of function calls.

However, in this example, every request reruns the entire series of function 
calls.
"""
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

"""Example 4

In this example, the view function uses a router model to execute its series 
of function calls and caches the result. See models.Router4 for more details.
"""
@app.route('/example4')
def example4():
    print('Request for /example4')
    router = get_model(Router4, 'router4')
    return router.route()

"""Example 5

Example 5 is similar to Example 4. See models.Router5 for more details.
"""
@app.route('/example5')
def example5():
    print('Request for /example5')
    router = get_model(Router5, 'router5')
    return router.route()

if __name__ == '__main__':
    socketio.run(app)
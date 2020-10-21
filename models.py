"""Database models"""

from factory import db

from flask_worker import Worker
from sqlalchemy_mutable import partial
from flask_worker import WorkerMixin

def complex_task(seconds):
    import time
    print('Complex task started')
    for i in range(seconds):
        print('Progress: {}%'.format(100.0*i/seconds))
        time.sleep(1)
    print('Progress: 100.0%')
    print('Complex task finished')
    return 'Hello, World!'


# create a Worker model with the worker mixin
class Worker(WorkerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __init__(self, name):
        super().__init__(func=partial(complex_task, seconds=5))
        self.name = name


def get_model(class_, name):
    return class_.query.filter_by(name=name).first() or class_(name)


from flask_worker import RouterMixin, set_route


class Router(RouterMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __init__(self, name):
        self.name = name
        super().__init__(self.func1, 'hello world')

    def func1(self, hello_world):
        print(hello_world)
        return self.func2('hello moon')

    # 'bookmark' functions with the `@set_route` decorator
    @set_route
    def func2(self, hello_moon):
        print(hello_moon)
        worker = get_model(Worker, 'routing')
        return self.func3('hello star') if worker.job_finished else worker()

    @set_route
    def func3(self, hello_star):
        print(hello_star)
        # optionally, reset the router
        # you may also want to reset Workers which were called by the Router
        self.reset()
        get_model(Worker, 'routing').reset()
        return 'Function calls finished.'
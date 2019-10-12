from factory import db

from flask_worker import RouterMixin, WorkerMixin, set_route

import time


class Router(RouterMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    def __init__(self):
        self.reset()

    def reset(self):
        self.current_route = 'route1'
        self.args = ['hello world']
        worker = Employer.query.first().worker
        worker.reset()

    def route1(self, hello_world):
        print(hello_world)
        return self.route2('hello moon')

    @set_route
    def route2(self, hello_moon):
        print(hello_moon)
        worker = Employer.query.first().worker
        return self.run_worker(
            worker, self.route3, args=['hello star']
        )

    def route3(self, hello_star):
        print(hello_star)
        self.reset()
        return 'Goodbye World'

class Employer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    worker = db.relationship('Worker', uselist=False, backref='employer')

    def complex_task(self, seconds):
        print('Complex task started')
        for i in range(seconds):
            time.sleep(1)
            print(i)
        print('Complex task finished')

    def __init__(self):
        self.worker = Worker(
            method_name='complex_task', kwargs={'seconds': 5}
        )

class Worker(WorkerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('employer.id'))
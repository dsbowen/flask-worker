from factory import db

from flask_worker import set_route, RouterMixin, WorkerMixin

import time


class Router(RouterMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    def __init__(self):
        self.default_route = 'route1'

    @set_route
    def route1(self):
        print('route1')
        return self.route2()

    @set_route
    def route2(self):
        print('route2')
        worker = Employer.query.first().worker
        return self.run_worker(worker, self.route3)

    @set_route
    def route3(self):
        print('route3')
        return 'Hello world'

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
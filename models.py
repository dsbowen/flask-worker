from factory import db

from flask_worker import WorkerMixin

import time

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
"""Database models

This file defines Employer and Worker models.

An Employer is a model with a complex task which must be run before a page 
loads. It employs a Worker to execute its complex task in the background. 
While working, the Worker sends the client a loading page.
"""

from factory import db

# 1. Import the worker mixin
from flask_worker import WorkerMixin

import time

def get_model(model_class, name):
    """Convenience method for database querying

    This function returns a model of the type model_class with the specified 
    name. If this model does not yet exist, this function creates it.
    """
    model = model_class.query.filter_by(name=name).first()
    if not model:
        model = model_class(name=name)
        db.session.add(model)
        db.session.flush([model])
    return model


class Employer(db.Model):
    """Employer model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # 2. Add a worker to the employer
    # The worker must reference its employer by the attribute name 'employer'
    worker = db.relationship('Worker', uselist=False, backref='employer')

    def __init__(self, name):
        self.name = name
        # 3. Instantiate a worker
        self.worker = Worker(
            method_name='complex_task', kwargs={'seconds': 5}
        )

    def complex_task(self, seconds):
        print('Complex task started')
        for i in range(seconds):
            print('Progress: {}%'.format(100.0*i/seconds))
            time.sleep(1)
        print('Progress: 100.0%')
        print('Complex task finished')


# 4. Create a Worker model with the worker mixin
class Worker(WorkerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('employer.id'))
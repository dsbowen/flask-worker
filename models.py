"""Database models

This file defines Employer and Worker models.

An Employer is a model with a complex task which must be run before a page 
loads. It employs a Worker to execute its complex task in the background. 
While working, the Worker sends the client a loading page.
"""

from factory import db

from flask_worker import WorkerMixin


class Employer(db.Model):
    """Employer model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # add a worker to the employer
    # the worker must reference its employer with an `employer` attribute
    worker = db.relationship('Worker', uselist=False, backref='employer')

    def __init__(self, name):
        self.name = name
        # instantiate a worker
        self.worker = Worker().set_method('complex_task', seconds=5)

    def complex_task(self, seconds=5):
        import time
        print('Complex task started')
        for i in range(seconds):
            print('Progress: {}%'.format(100.0*i/seconds))
            time.sleep(1)
        print('Progress: 100.0%')
        print('Complex task finished')


# create a Worker model with the worker mixin
class Worker(WorkerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('employer.id'))


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
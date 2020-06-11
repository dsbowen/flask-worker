# Employers and workers

Flask-Worker uses what I call an 'Employer-Worker' model. An Employer is a class which needs to execute a complex (i.e. long-running) task before a view function returns a page to the client. A Worker executes the Employer's complex task by sending it to a Redis queue. While the client is waiting for the complex task to finish, the Worker sends the client a loading page.

We'll create the Employer and Worker models in a file called `models.py`. Our folder now looks like:

```
factory.py
models.py
```

```python
from factory import db

from flask_worker import WorkerMixin


class Employer(db.Model):
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


class Worker(WorkerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('employer.id'))
```

We'll also define a convenience method at the bottom of this file for database querying. This function returns a model of the type `model_class` with the specified `name`. If this model does not yet exist, this function creates it.

```python
...
def get_model(model_class, name):
    model = model_class.query.filter_by(name=name).first()
    if not model:
        model = model_class(name=name)
        db.session.add(model)
        db.session.flush([model])
    return model
```
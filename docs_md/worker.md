# Workers

A Worker executes a complex task by sending it to a Redis queue. While the client is waiting for the complex task to finish, the Worker sends the client a loading page.

We'll create the Worker model in a file called `models.py`. Our folder now looks like:

```
factory.py
models.py
```

```python
from factory import db

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
        self.name = name
        # set the worker's complex task along with args and kwargs
        self.set(complex_task, seconds=5)
        super().__init__()
```

We'll also define a convenience method at the bottom of this file for database querying. This function returns a model of the type `class_` with the specified `name`. If this model does not yet exist, this function creates it.

```python
...
def get_model(class_, name):
    return class_.query.filter_by(name=name).first() or class_(name)
```
# View functions

Now we can use the Worker in our view functions. 

## Setup

By default, the `Manager` expects the Flask application to be an object named `app` in a file in the root directory called `app.py`. (You can change this by setting the Manager's `app_import` attribute). For the tutorial, we'll stick with the default. Our folder looks like:

```
static/
    worker_loading.gif
app.py
factory.py
models.py
```

All of the code in this part of the tutorial goes in the `app.py` file.

```python
from factory import create_app, db, socketio
from models import Worker, get_model

app = create_app()

# create database before first app request
@app.before_first_request
def before_first_request():
    db.create_all()

# VIEW FUNCTIONS GO HERE

if __name__ == '__main__':
    socketio.run(app, debug=True)
```

## Basic use

This is a basic example in which the Worker executes its complex task.

The Worker only sends its complex task to the Redis Queue once, regardless of how many times the client requests this route. Until the Worker finishes its job, it returns a loading page. The result is cached once the Worker finishes its job, so that future calls to this route will not re-run the complex task.

```python
@app.route('/')
@app.route('/index')
def index():
    worker = get_model(Worker, 'index')
    return worker.result if worker.job_finished else worker()
```

We are now ready to [run our app](run.md). 

## Resetting a Worker

In this example, we reset the Worker after it has finished its job. This means that future calls to this route *will* re-run the complex task.

```python
@app.route('/reset')
def with_reset():
    worker = get_model(Worker, 'reset')
    if not worker.job_finished:
        return worker()
    worker.reset()
    db.session.commit()
    return worker.result
```

## Callback routes

This example demonstrates how to use a Worker's `callback` function. By default, when a Worker finishes its job, it issues another call to the current view function. Set the worker's `callback` attribute to the name of another view function to redirect the client after the Worker finishes its job.

```python
@app.route('/callback')
def with_callback():
    worker = get_model(Worker, 'callback')
    worker.callback = 'callback_route'
    if worker.job_finished:
        worker.reset()
    return worker()

@app.route('/callback_route')
def callback_route():
    worker = get_model(Worker, 'callback')
    return worker.result if worker.job_finished else worker()
```
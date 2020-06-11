# View functions

Now we can use the Employer and Worker in our view functions. 

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
from models import Employer, get_model

app = create_app()

@app.before_first_request
def before_first_request():
    db.create_all()

# VIEW FUNCTIONS GO HERE

if __name__ == '__main__':
    socketio.run(app, debug=True)
```

## Basic use

This is a basic example in which the Employer uses its Worker to execute its complex task.

The Worker only sends the Employer's complex task to the Redis Queue once, regardless of how many times the client requests this route. Until the Worker finishes its job, it returns a loading page. The result is cached once the Worker finishes its job, so that future calls to this route will not re-run the complex task.

```python
@app.route('/')
@app.route('/index')
def basic():
    print('Request for /index')
    employer = get_model(Employer, 'index')
    worker = employer.worker
    if not worker.job_finished:
        return worker()
    return 'Complex task finished.'
```

We are now ready to [run our app](run.md). 

## Resetting a Worker

In this example, we reset the Worker after it has finished its job. This means that future calls to this route *will* re-run the complex task.

```python
@app.route('/reset')
def with_reset():
    print('Request for /reset')
    employer = get_model(Employer, 'reset')
    worker = employer.worker
    if not worker.job_finished:
        return worker()
    worker.reset()
    db.session.commit()
    return 'Complex task finished. Reload the page to execute the task again.'
```

## Callback routes

This example demonstrates how to use a Worker's `callback` function. By default, when a Worker finishes its job, it issues another call to the current view function. Set the worker's `callback` attribute to the name of another view function to redirect the client after the Worker finishes its job.

```python
@app.route('/callback')
def with_callback():
    print('Request for /callback')
    employer = get_model(Employer, 'callback')
    worker = employer.worker
    worker.callback = 'callback_route'
    return worker()

@app.route('/callback_route')
def callback_route():
    print('Request for /callback_route')
    employer = get_model(Employer, 'callback')
    worker = employer.worker
    if not worker.job_finished:
        return worker()
    worker.reset()
    db.session.commit()
    return 'This is the callback route.'
```
Flask-Worker simplifies interaction with a [Redis Queue](https://redis.io/) for executing long-running tasks in a [Flask](https://flask.palletsprojects.com/en/1.1.x/) application. 

Long-running tasks are managed by a Worker, who sends the client a loading page until it completes the task. Upon completing the task, the Worker automatically replaces the client's window with the loaded page.

## Why Flask-Worker

Suppose we have a view function which needs to execute a complex task before the client can view the page. What we want is for the complex task to run once, and for the view function to return a loading page while the complex task is running. Our first pass might be:

```python
@app.route('/')
def index():
    return complex_task()
```

Unfortunately, the view function executes the complex task every time it is called. To make matters worse, the client has no indication that the complex task is in progress. Each time the client tries to refresh the page, the complex task is queued up again.

Flask-Worker solves this problem. We set up a Worker:

```python
class Worker(WorkerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __init__(self, name):
        self.name = name
        self.set(complex_task)
        super().__init__()
```

And call it in a view function:

```python
@app.route('/')
def index():
    worker = get_model(Worker, name='index')
    return worker.result if worker.job_finished else worker()
```

See the [tutorial](https://dsbowen.github.io/flask-worker/factory/) for a complete example.

## Installation

```
$ pip install flask-worker
```

## Citation

```
@software{bowen2020flask-worker,
  author = {Dillon Bowen},
  title = {Flask-Worker},
  url = {https://dsbowen.github.io/flask-worker/},
  date = {2020-06-15},
}
```

## License

Users must cite this package in any publications which use it.

It is licensed with the MIT [License](https://github.com/dsbowen/flask-worker/blob/master/LICENSE).
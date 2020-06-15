# Routers

## The problem

Suppose we want a view function to execute a series of function calls. During these function calls, the Worker executes its complex task. Our first pass might be to add something like the following in `app.py`.

```python
@app.route('/no-router')
def no_router():
    return func1('hello world')

def func1(hello_world):
    print(hello_world)
    return func2('hello moon')

def func2(hello_moon):
    print(hello_moon)
    worker = get_model(Worker, 'no_router')
    return func3(worker.result) if worker.job_finished else worker()

def func3(hello_star):
    print(hello_star)
    db.session.commit()
    return 'Function calls finished.'
```

The problem is that the entire series of function calls executes every time this view function is called. However, it may be important that we do not call `func1` a second time.

Ideally, we want to 'pause' the series of function calls while the complex task is executing. Once the worker has finished its job, we want to pick up where we left off.

## The solution

A Router solves this problem by managing a series of function calls initiated by a view function. The Router tracks function calls and their arguments. It does this by 'bookmarking' its methods with the `@set_route` decorator.

We'll put the following code at the bottom of our a `models.py` file.

```python
from flask_worker import RouterMixin, set_route


class Router(RouterMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __init__(self, name):
        self.name = name
        super().__init__(self.func1, 'hello world')

    def func1(self, hello_world):
        print(hello_world)
        return self.func2('hello moon')

    # 'bookmark' functions with the `@set_route` decorator
    @set_route
    def func2(self, hello_moon):
        print(hello_moon)
        worker = get_model(Worker, 'routing')
        return self.func3('hello star') if worker.job_finished else worker()

    @set_route
    def func3(self, hello_star):
        print(hello_star)
        # optionally, reset the router
        self.reset()
        # you may also want to reset Workers which were called by the Router
        get_model(Worker, 'routing').reset()
        return 'Function calls finished.'
```

We'll also create a view function for the Router in `app.py`.

```python
from models import Router

@app.route('/router')
def routing():
    return get_model(Router, 'routing')()
```

Note that we reset the Router and the Worker it used in `func3`. If we had not reset it, the Router would have cached the result of the function calls. Try commenting out those two lines of code and rerunning your app.
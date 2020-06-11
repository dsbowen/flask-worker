# Routers

## The problem

Suppose we want a view function to execute a series of function calls. During these function calls, the Employer's complex task is executed. Our first pass might be to add something like the following in `app.py`.

```python
@app.route('/no-router')
def no_router():
    print('Request for /no-router')
    return func1('hello world')

def func1(hello_world):
    print(hello_world)
    return func2('hello moon')

def func2(hello_moon):
    print(hello_moon)
    employer = get_model(Employer, 'no-router')
    employer.complex_task(seconds=5)
    return func3('hello star')

def func3(hello_star):
    print(hello_star)
    db.session.commit()
    return 'Function calls finished.'
```

The problem is that the entire series of function calls executes every time this view function is called.

Ideally, we want to 'pause' the series of function calls while the complex task is executing. Once the worker has finished its job, we want to pick up where we left off.

## The solution

A Router solves this problem by managing a series of function calls initiated by a view function.

The Router tracks function calls and their arguments. It does this by 'bookmarking' its methods with the `@set_route` decorator. It also has a dedicated method for using a Worker to run an Employer's complex task.

We'll put the following code in a `router_models.py` file. Our folder looks like:

```
static/
    worker_loading.gif
app.py
factory.py
models.py
router_models.py
```

```python
from factory import db
from models import Employer, get_model

from flask_worker import RouterMixin, set_route


# create a Router class with the router mixin.
class Router(RouterMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __init__(self, name):
        self.name = name
        # set `current_route` on initialization
        self.current_route = 'func1'
        self.args = ['hello world']
        super().__init__()

    def func1(self, hello_world):
        print(hello_world)
        return self.func2('hello moon')

    # 'bookmark' functions with the `@set_route` decorator
    @set_route
    def func2(self, hello_moon):
        print(hello_moon)
        employer = get_model(Employer, 'basic_routing')
        worker = employer.worker
        # run the Employer's complex task with a Worker
        return self.run_worker(worker, self.func3, 'hello star')

    @set_route
    def func3(self, hello_star):
        print(hello_star)
        return 'Function calls finished.'
```

We'll also create a view function for the Router in `app.py`.

```python
from router_models import Router

@app.route('/router')
def basic_routing():
    print('Request for /router')
    router = get_model(Router, 'router')
    return router.route()
```

## Resetting a router

In the previous example, we bookmarked the final function call. This means that any future calls to this Router will bypass the series of function calls, going straight to the final function call. This is sometimes, but not always, desirable behavior.

This example resets the Router. Future calls to this Router will re-execute the entire series of function calls.

Add the following to `router_models.py`.

```python
class RouterWithReset(RouterMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __init__(self, name):
        self.name = name
        self.reset()
        super().__init__()

    def reset(self):
        self.current_route = 'func1'
        self.args, self.kwargs = ['hello world'], {}
        employer = get_model(Employer, 'routing_with_reset')
        employer.worker.reset()

    def func1(self, hello_world):
        print(hello_world)
        return self.func2('hello moon')

    @set_route
    def func2(self, hello_moon):
        print(hello_moon)
        employer = get_model(Employer, 'routing_with_reset')
        worker = employer.worker
        return self.run_worker(worker, self.func3, 'hello star')

    def func3(self, hello_star):
        print(hello_star)
        self.reset()
        return '''
            Function calls finished. Reload the page to execute the 
            function calls again.
        '''
```

Add the following to `app.py`.

```python
from router_models import RouterWithReset

@app.route('/router-reset')
def routing_with_reset():
    print('Request for /router-reset')
    router = get_model(RouterWithReset, 'router_reset')
    return router.route()
```
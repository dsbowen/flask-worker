"""Router models

A Router manager a series of function calls initiated by a view function. 
Among this series of function calls is the Employer's complex task.

The Router tracks the function calls and their arguments. It uses a Worker to 
run the Employer's complex task. Once the complex task is finished, the 
Router picks up the series of function calls where it left off. 
"""

from factory import db
from models import Employer, get_model

# 1. Import the router mixin and set_route decorator
from flask_worker import RouterMixin, set_route

# 2. Create a Router class with the router mixin.
class Router4(RouterMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __init__(self, name):
        self.name = name
        # 3. Set `current_route` on initialization
        self.current_route = 'func1'
        self.args = ['hello world']
        super().__init__()

    def func1(self, hello_world):
        print(hello_world)
        return self.func2('hello moon')

    # 4. 'Bookmark' functions with the @set_route decorator
    @set_route
    def func2(self, hello_moon):
        print(hello_moon)
        employer = get_model(Employer, 'employer4')
        worker = employer.worker
        # 5. Run the Employer's complex task with a Worker
        return self.run_worker(
            worker=worker, next_route=self.func3, args=['hello star']
        )

    @set_route
    def func3(self, hello_star):
        print(hello_star)
        return 'Example 4 finished'


class Router5(RouterMixin, db.Model):
    """
    Router5 is similar to Router4. However, once Router5 finishes 
    its function calls, it resets. If its route method is called after the 
    function calls have finished, Router5 will rerun its series of function 
    calls. 
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __init__(self, name):
        self.name = name
        self.reset()
        super().__init__()

    def reset(self):
        self.current_route = 'func1'
        self.args = ['hello world']
        self.kwargs = {}
        employer = get_model(Employer, 'employer5')
        employer.worker.reset()

    def func1(self, hello_world):
        print(hello_world)
        return self.func2('hello moon')

    @set_route
    def func2(self, hello_moon):
        print(hello_moon)
        employer = get_model(Employer, 'employer5')
        worker = employer.worker
        return self.run_worker(
            worker=worker, next_route=self.func3, args=['hello star']
        )

    def func3(self, hello_star):
        print(hello_star)
        # 6. (Optional) Reset the Router
        self.reset()
        return 'Example 5 finished'
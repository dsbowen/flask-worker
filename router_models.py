"""Router models"""

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
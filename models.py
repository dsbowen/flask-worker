from factory import db

from flask_worker import RouterMixin, WorkerMixin, set_route

import time

def get_model(model_class, name):
    model = model_class.query.filter_by(name=name).first()
    if not model:
        model = model_class(name=name)
        db.session.add(model)
        db.session.flush([model])
    return model


class Employer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    worker = db.relationship('Worker', uselist=False, backref='employer')

    def __init__(self, name):
        self.name = name
        self.worker = Worker(
            method_name='complex_task', kwargs={'seconds': 5}
        )

    def complex_task(self, seconds):
        print('Complex task started')
        for i in range(seconds):
            print('Progress: {}%'.format(100.0*i/seconds))
            time.sleep(1)
        print('Progress: 100.0%')
        print('Complex task finished')


class Worker(WorkerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('employer.id'))


class Router4(RouterMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __init__(self, name):
        self.name = name
        self.current_route = 'func1'
        self.args = ['hello world']
        super().__init__()

    def func1(self, hello_world):
        print(hello_world)
        return self.func2('hello moon')

    @set_route
    def func2(self, hello_moon):
        print(hello_moon)
        employer = get_model(Employer, 'employer4')
        worker = employer.worker
        return self.run_worker(
            worker=worker, next_route=self.func3, args=['hello star']
        )

    @set_route
    def func3(self, hello_star):
        print(hello_star)
        db.session.commit()
        return 'Example 4 finished'


class Router5(RouterMixin, db.Model):
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
        self.reset()
        db.session.commit()
        return 'Example 5 finished'
"""Worker Mixin

The worker executes a complex task for its employer using a Redis queue. 

When called, it enqueues a job (one of its employer's methods specified by 
`method_name`). The worker returns a loading page, specified by its 
`template`. The default loading template displays a loading image (specified 
by `loading_img`). The worker looks for the loading image in the app's static
folder, or if `blueprint` is set, in the blueprint's static folder.

When a Redis worker grabs the enqueued job, it executes it with the worker's 
args and kwargs. After execution, the worker's script replaces the client's 
window location with a call to its `callback` view function.
"""

from bs4 import BeautifulSoup
from flask import Markup, current_app, render_template, request
from sqlalchemy import Boolean, Column, String
from sqlalchemy.inspection import inspect
from sqlalchemy_mutable import MutableListType, MutableDictType


class WorkerMixin():
    method_name = Column(String)
    args = Column(MutableListType)
    kwargs = Column(MutableDictType)
    callback = Column(String)
    job_finished = Column(Boolean, default=False)
    job_in_progress = Column(Boolean, default=False)
    job_id = Column(String)
    _blueprint = Column(String)
    _loading_img = Column(String)
    _template = Column(String)

    @property
    def blueprint(self):
        default_blueprint = current_app.extensions['manager'].blueprint
        return self._blueprint or default_blueprint

    @blueprint.setter
    def blueprint(self, value):
        self._blueprint = value
    
    @property
    def loading_img(self):
        default_img = current_app.extensions['manager'].loading_img
        return self._loading_img or default_img

    @property
    def static_folder(self):
        blueprint = self.blueprint+'.' if self.blueprint is not None else ''
        return blueprint+'static'
    
    @loading_img.setter
    def loading_img(self, value):
        self._loading_img = value
    
    @property
    def template(self):
        default_template = current_app.extensions['manager'].template
        return self._template or default_template
    
    @template.setter
    def template(self, value):
        self._template = value

    @property
    def model_id(self):
        return self.__class__.__name__+'-'+str(self.get_id())

    def __init__(
            self, method_name=None, args=[], kwargs={}, callback=None,
            blueprint=None, loading_img=None, template=None, 
            *init_args, **init_kwargs
        ):
        self.method_name = method_name
        self.args = args
        self.kwargs = kwargs
        self.callback = callback
        self.blueprint = blueprint
        self.loading_img = loading_img
        self.template = template
        self.reset()
        super().__init__(*init_args, **init_kwargs)
    
    def __call__(self):
        if self.get_id() is None:
            db = current_app.extensions['manager'].db
            db.session.add(self)
            db.session.commit()
        if not self.job_in_progress:
            self.enqueue()
        html = render_template(self.template, worker=self)
        return BeautifulSoup(html, 'html.parser').prettify()

    def get_id(self):
        id = inspect(self).identity
        if id:
            return id[0]
        return None

    def enqueue(self):
        """Send a job to the Redis Queue"""
        job = current_app.task_queue.enqueue(
            'flask_worker.tasks.execute',
            kwargs={
                'app_import': current_app.extensions['manager'].app_import,
                'worker_class': type(self), 
                'worker_id': self.get_id()
            }
        )
        self.job_finished, self.job_in_progress = False, True
        self.job_id = job.get_id()
        db = current_app.extensions['manager'].db
        db.session.commit()

    def script(self):
        """Return the worker script
        
        Include this in the `scripts` block of the loading template.
        """
        callback = self.callback or request.url
        return Markup(render_template(
            'worker/worker_script.html', 
            worker=self, 
            callback_url=callback
        ))

    def execute_job(self):
        """Execute a job (i.e. its employer's task)

        This method is called by a Redis worker.
        """
        if self.employer is not None and self.method_name is not None:
            func = getattr(self.employer, self.method_name)
            result = func(*self.args, **self.kwargs)
        else:
            result = None
        self.job_finished, self.job_in_progress = True, False
        return result

    def reset(self):
        self.job_finished, self.job_in_progress = False, False
        self.job_id = None
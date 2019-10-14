"""Worker Mixin

The worker executes a complex task for its employer using a Redis queue. 

When called, it enqueues a job (one of its employer's methods specified by 
`method_name`). The worker returns a loading page, specified by its 
`template`. The default loading template displays a loading image (specified 
by `loading_img`).

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
    _template = Column(String)
    callback = Column(String)
    job_finished = Column(Boolean, default=False)
    job_in_progress = Column(Boolean, default=False)
    job_id = Column(String)
    _loading_img = Column(String)

    @property
    def template(self):
        default_template = current_app.extensions['manager'].template
        return self._template or default_template
    
    @template.setter
    def template(self, value):
        self._template = value
    
    @property
    def loading_img(self):
        default_img = current_app.extensions['manager'].loading_img
        return self._loading_img or default_img
    
    @loading_img.setter
    def loading_img(self, value):
        self._loading_img = value

    @property
    def model_id(self):
        return self.__class__.__name__+'-'+str(inspect(self).identity[0])

    def __init__(
            self, method_name=None, args=[], kwargs={}, 
            template=None, callback=None, loading_img=None,
            *init_args, **init_kwargs
        ):
        self.method_name = method_name
        self.args = args
        self.kwargs = kwargs
        self.template = template
        self.callback = callback
        self.loading_img = loading_img
        self.reset()
        super().__init__(*init_args, **init_kwargs)
    
    def __call__(self):
        if not self.job_in_progress:
            self.enqueue()
        html = render_template(self.template, worker=self)
        return BeautifulSoup(html, 'html.parser').prettify()

    def enqueue(self):
        """Send a job to the Redis Queue"""
        worker_id = inspect(self).identity[0]
        job = current_app.task_queue.enqueue(
            'flask_worker.tasks.execute',
            kwargs={
                'app_import': current_app.extensions['manager'].app_import,
                'worker_class': type(self), 
                'worker_id': worker_id}
        )
        self.job_finished, self.job_in_progress = False, True
        self.job_id = job.get_id()
        db = current_app.extensions['manager'].db
        db.session.commit()

    def script(self):
        """Return the worker script
        
        Include this in the `scripts` block of the loading template.
        """
        callback = self.callback or request.url_rule
        return Markup(render_template(
            'worker_script.html', worker=self, callback_url=callback
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
"""Worker Mixin"""

from bs4 import BeautifulSoup
from flask import Markup, current_app, render_template, request
from sqlalchemy import Boolean, Column, String
from sqlalchemy.inspection import inspect
from sqlalchemy_mutable import MutableListType, MutableDictType


class WorkerMixin():
    method_name = Column(String)
    args = Column(MutableListType)
    kwargs = Column(MutableDictType)
    template = Column(String)
    callback = Column(String)
    job_finished = Column(Boolean, default=False)
    job_in_progress = Column(Boolean, default=False)
    job_id = Column(String)
    loading_img = Column(String)

    @property
    def model_id(self):
        return self.__class__.__name__+'-'+str(inspect(self).identity[0])

    @property
    def ready_to_work(self):
        return not (self.job_in_progress or self.job_finished)

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
        template = self.template or 'worker_loading.html'
        html = render_template(template, worker=self)
        return BeautifulSoup(html, 'html.parser').prettify()

    def enqueue(self):
        worker_id = inspect(self).identity[0]
        job = current_app.task_queue.enqueue(
            current_app.extensions['manager'].execute,
            kwargs={'worker_class': type(self), 'worker_id': worker_id}
        )
        self.job_finished, self.job_in_progress = False, True
        self.job_id = job.get_id()
        db = current_app.extensions['manager'].db
        db.session.commit()

    def script(self):
        callback = self.callback or request.url_rule
        return Markup(render_template(
            'worker_script.html', worker=self, callback_url=callback
        ))

    def execute_job(self):
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
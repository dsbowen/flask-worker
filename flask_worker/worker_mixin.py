"""Worker Mixin

The worker executes a complex task for its employer using a Redis queue. 

When called, it enqueues a job (one of its employer's methods specified by 
`method_name`). The worker returns a loading page, specified by its 
`loading_page`.

When a Redis worker grabs the enqueued job, it executes it with the worker's 
`args` and `kwargs`. After execution, the worker's script replaces the 
client's window location with a call to its `callback` view function.
"""

from bs4 import BeautifulSoup
from flask import current_app, render_template, request
from sqlalchemy import Boolean, Column, String
from sqlalchemy.inspection import inspect
from sqlalchemy_modelid import ModelIdBase
from sqlalchemy_mutable import MutableListType, MutableDictType
from sqlalchemy_mutablesoup import MutableSoupType


class WorkerMixin(ModelIdBase):
    method_name = Column(String)
    args = Column(MutableListType)
    kwargs = Column(MutableDictType)
    callback = Column(String)
    job_finished = Column(Boolean, default=False)
    job_in_progress = Column(Boolean, default=False)
    job_id = Column(String)
    loading_page = Column(MutableSoupType)

    @property
    def manager(self):
        return current_app.extensions['manager']

    """HTML attributes"""
    @property
    def loading_img(self):
        return self.loading_page.select_one('img')

    @property
    def loading_img_src(self):
        return self.loading_img.attrs.get('src')

    @loading_img_src.setter
    def loading_img_src(self, src):
        self.loading_img['src'] = src or ''
        self.loading_img.changed()

    def __init__(self, template=None, *args, **kwargs):
        template = template or self.manager.template
        self.loading_page = render_template(template, worker=self)
        self.reset()
        self.args, self.kwargs = [], {}
        [setattr(self, key, val) for key, val in kwargs.items()]
        super().__init__(*args, **kwargs)
    
    def __call__(self):
        if self.get_id() is None:
            db = self.manager.db
            db.session.add(self)
            db.session.commit()
        if not self.job_in_progress:
            self.enqueue()
        self.add_script()
        return str(self.loading_page)

    def get_id(self):
        id = inspect(self).identity
        return id[0] if id else None

    def enqueue(self):
        """Send a job to the Redis Queue"""
        job = current_app.task_queue.enqueue(
            'flask_worker.tasks.execute',
            kwargs={
                'app_import': self.manager.app_import,
                'worker_class': type(self), 
                'worker_id': self.get_id()
            }
        )
        self.job_finished, self.job_in_progress = False, True
        self.job_id = job.get_id()
        self.manager.db.session.commit()

    def add_script(self):
        """Add the worker script to the loading page"""
        script_html = render_template(
            'worker/worker_script.html',
            worker=self,
            callback_url=(self.callback or request.url)
        )
        script = BeautifulSoup(script_html, 'html.parser')
        self.loading_page.select_one('head').append(script)

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
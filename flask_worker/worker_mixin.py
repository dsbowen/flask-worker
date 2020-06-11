"""# Workers"""

from bs4 import BeautifulSoup
from flask import current_app, render_template, request
from sqlalchemy import Boolean, Column, String
from sqlalchemy.inspection import inspect
from sqlalchemy_modelid import ModelIdBase
from sqlalchemy_mutable import MutableListType, MutableDictType
from sqlalchemy_mutablesoup import MutableSoupType


class WorkerMixin(ModelIdBase):
    """
    The worker executes a complex task for its `employer` using a Redis queue. 

    When called, it enqueues a job (one of its employer's methods specified by 
    `method_name`). The worker returns a loading page, specified by its 
    `loading_page`.

    When a Redis worker grabs the enqueued job, it executes it with the 
    worker's `args` and `kwargs`. After execution, the worker's script 
    replaces the client's window location with a call to its `callback` view 
    function.

    Parameters
    ----------
    template : str or None, default=None
        Name of the html template file for the worker's loading page. If 
        `None`, the worker will use the manager's loading page template.

    \*\*kwargs :
        You can set the worker's attributes by passing them as keyword 
        arguments.

    Attributes
    ----------
    manager : flask_worker.Manager
        The worker's manager.

    method_name : str
        Name of the employer's method which the worker will execute.

    args : list, default=[]
        Arguments which will be passed to the executed method.

    kwargs : dict, default={}
        Keyword arguments which will be passed to the executed method.

    callback : str or None, default=None
        Name of the view function to which the client will navigate once the 
        worker has finished its job. If `None`, the current view function is 
        re-called.

    job_finished : bool, default=False
        Indicates that the worker has finished its job.

    job_in_progress : bool, default=False
        Indicates that the worker has a job in progress.

    job_id : str
        Identifier for the worker's job.

    loading_page : sqlalchemy_mutablesoup.MutableSoup
        Loading page which will be displayed to the client while the worker performs its job.

    loading_img : bs4.Tag
        `<img>` tag for the loading image.

    loading_img_src : str
        Source of the loading image.
    """
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

    def set_method(self, method_name, *args, **kwargs):
        """
        Set the worker's `method_name` attribute.

        Parameters
        ----------
        method_name : str
            Name of the employer's method which the worker executes.

        \*args, \*\*kwargs :
            Arguments and keyword arguments for the method.

        Returns
        -------
        self : flask_worker.WorkerMixin
        """
        self.method_name = method_name
        self.args, self.kwargs = list(args), kwargs
        return self

    def reset(self):
        """
        Clears the `job_finished`, `job_in_progress`, and `job_id` attributes.

        Returns
        -------
        self : flask_worker.WorkerMixin
        """
        self.job_finished, self.job_in_progress = False, False
        self.job_id = None
        return self
    
    def __call__(self):
        """
        Enqueue the employer's job for execution if it is not enqueued already.

        Returns
        -------
        loading_page : str (html)
            The client's loading page.
        """
        if self._get_id() is None:
            db = self.manager.db
            db.session.add(self)
            db.session.commit()
        if not self.job_in_progress:
            self._enqueue()
        self._add_script()
        return str(self.loading_page)

    def _get_id(self):
        id = inspect(self).identity
        return id[0] if id else None

    def _enqueue(self):
        """Send a job to the Redis Queue"""
        job = current_app.task_queue.enqueue(
            'flask_worker.tasks.execute',
            kwargs={
                'app_import': self.manager.app_import,
                'worker_class': type(self), 
                'worker_id': self._get_id()
            }
        )
        self.job_finished, self.job_in_progress = False, True
        self.job_id = job.get_id()
        self.manager.db.session.commit()

    def _add_script(self):
        """Add the worker script to the loading page"""
        script_html = render_template(
            'worker/worker_script.html',
            worker=self,
            callback_url=(self.callback or request.url)
        )
        script = BeautifulSoup(script_html, 'html.parser')
        self.loading_page.select_one('head').append(script)

    def _execute_job(self):
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
"""# Workers"""

from bs4 import BeautifulSoup
from flask import current_app, render_template, request
from sqlalchemy import Boolean, Column, PickleType, String
from sqlalchemy.inspection import inspect
from sqlalchemy_function import FunctionMixin
from sqlalchemy_modelid import ModelIdBase
from sqlalchemy_mutablesoup import MutableSoupType


class WorkerMixin(FunctionMixin, ModelIdBase):
    """
    The worker executes a complex task using a Redis queue. When called, it 
    enqueues a job and returns a loading page.

    When a Redis worker grabs the enqueued job, it executes the worker's 
    function, `func`, passing in the worker's `args` and `kwargs`. After 
    execution, the worker's script replaces the client's window location with 
    a call to its `callback` view function.

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

    func : callable
        Function which the worker will execute.

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

    result :
        Output of the worker's function. This stores the result of the job 
        the worker executed.
    """
    callback = Column(String)
    job_finished = Column(Boolean, default=False)
    job_in_progress = Column(Boolean, default=False)
    job_id = Column(String)
    loading_page = Column(MutableSoupType)
    result = Column(PickleType)

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

    def __init__(self, template=None, **kwargs):
        template = template or self.manager.template
        self.loading_page = render_template(template, worker=self)
        self.reset()
        self.args, self.kwargs = self.args or [], self.kwargs or {}
        [setattr(self, key, val) for key, val in kwargs.items()]
        super().__init__(self.func)

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
        Enqueue the worker's job for execution if it is not enqueued already.

        Returns
        -------
        loading_page : str (html)
            The client's loading page.
        """
        if self._get_id() is None:
            session = self.manager.db.session
            session.add(self)
            session.commit()
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
        """Execute a job (i.e. the worker's task)

        This method is called by a Redis worker.
        """
        self.result = super().__call__()
        self.job_finished, self.job_in_progress = True, False
        return self.result
"""# Workers"""

from flask import current_app, render_template, request
from sqlalchemy import Boolean, Column, String
from sqlalchemy.inspection import inspect
from sqlalchemy_modelid import ModelIdBase
from sqlalchemy_mutable import MutableType


class WorkerMixin(ModelIdBase):
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
    _callback = Column(String)
    func = Column(MutableType)
    job_finished = Column(Boolean, default=False)
    job_in_progress = Column(Boolean, default=False)
    job_id = Column(String)
    template = Column(String)
    loading_img_src = Column(String)
    result = Column(MutableType)

    @property
    def callback(self):
        if self._callback:
            return self._callback
        try:
            # if operating in request context
            return request.url
        except:
            # operating outside request context
            return self._callback

    @callback.setter
    def callback(self, val):
        self._callback = val

    @property
    def manager(self):
        return current_app.extensions['manager']

    def __init__(
            self, func, callback=None, template=None, loading_img_src=None
        ):
        self.func = func
        self.callback = callback
        self.template = template or self.manager.template
        self.loading_img_src = loading_img_src or self.manager.loading_img_src
        self.reset()
        super().__init__()

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
    
    def __call__(self, *args, **kwargs):
        """
        Enqueue the worker's job for execution if it is not enqueued already.

        Returns
        -------
        loading_page : str (html)
            The client's loading page.
        """
        def enqueue():
            job = current_app.task_queue.enqueue(
                'flask_worker.tasks.execute',
                kwargs=dict(
                    app_import=self.manager.app_import,
                    worker_class=self.__class__, 
                    worker_id=self._get_id(),
                    args=args, kwargs=kwargs
                )
            )
            self.job_finished, self.job_in_progress = False, True
            self.job_id = job.get_id()

        if self._get_id() is None:
            session = self.manager.db.session
            session.add(self)
            session.commit()
        if not self.job_in_progress:
            enqueue()
            self.manager.db.session.commit()
        return render_template(self.template, worker=self)

    def _get_id(self):
        id = inspect(self).identity
        return id[0] if id else None

    def _execute_job(self, *args, **kwargs):
        """Execute a job (i.e. the worker's task)

        This method is called by a Redis worker.
        """
        self.result = self.func(*args, **kwargs)
        self.job_finished, self.job_in_progress = True, False
        return self.result
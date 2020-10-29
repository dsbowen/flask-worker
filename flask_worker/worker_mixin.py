"""# Workers"""

from flask import current_app, render_template, request
from sqlalchemy import Boolean, Column, String
from sqlalchemy.inspection import inspect
from sqlalchemy_modelid import ModelIdBase
from sqlalchemy_mutable import MutableType


def enqueue(enqueue_method):
    # wraps the worker's enqueueing methods
    def enqueue_wrapper(worker, *args, **kwargs):
        if inspect(worker).identity is None:
            # ensure the worker has an id
            session = worker.manager.db.session
            session.add(worker)
            session.commit()
        if not worker.job_in_progress:
            # avoid repeat enqueuing
            job = enqueue_method(worker, *args, **kwargs)
            worker.job_finished, worker.job_in_progress = False, True
            worker.job_id = job.get_id()
            worker.manager.db.session.commit()
        # return the loading page HTML
        return render_template(worker.template, worker=worker)

    return enqueue_wrapper


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
    callback : str or None, default=None
        Name of the view function to which the client will navigate once the 
        worker has finished its job. If `None`, the current view function is 
        re-called.

    template : str or None, default=None
        Name of the html template file for the worker's loading page. If 
        `None`, the worker will use the manager's loading page template.

    loading_img_src : str or None, default=None
        Source of the loading image. If `None` the worker will use the 
        manager's loading image.

    Attributes
    ----------
    callback : str
        Set from the `callback` parameter.

    template : str
        Set from the `template` parameter.

    loading_img_src : str
        Set from the `loading_img_src` parameter.

    manager : flask_worker.Manager
        The worker's manager.

    job_finished : bool, default=False
        Indicates that the worker has finished its job.

    job_in_progress : bool, default=False
        Indicates that the worker has a job in progress.

    job_id : str
        Identifier for the worker's job.
    """
    _callback = Column(String)
    job_finished = Column(Boolean, default=False)
    job_in_progress = Column(Boolean, default=False)
    job_id = Column(String)
    template = Column(String)
    loading_img_src = Column(String)

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

    def __init__(self, callback=None, template=None, loading_img_src=None):
        self.callback = callback
        self.template = template or self.manager.template
        self.loading_img_src = loading_img_src or self.manager.loading_img_src
        self.reset()
        super().__init__()

    def reset(self):
        """
        Resets the `job_finished`, `job_in_progress`, and `job_id` attributes.

        Returns
        -------
        self :
        """
        self.job_finished, self.job_in_progress = False, False
        self.job_id = None
        return self

    @enqueue
    def enqueue_method(self, model, method_name, *args, **kwargs):
        """
        Enqueue a database model's method for execution.

        Parameters
        ----------
        model : db.Model
            Model whose method will be enqueued.

        method_name : str
            Name of the model's method to enqueue.

        \*args, \*\*kwargs :
            Arguments and keyword arguments passed to the method.

        Returns
        -------
        loading_page : str (html)
            The client's loading page.
        """
        return current_app.task_queue.enqueue(
            'flask_worker.tasks.execute_method',
            kwargs=dict(
                app_import=self.manager.app_import,
                worker_cls=self.__class__, 
                worker_id=inspect(self).identity[0],
                model_cls=type(model),
                model_id=inspect(model).identity[0],
                method_name=method_name, args=args, kwargs=kwargs
            )
        )
    
    @enqueue
    def enqueue_function(self, func, *args, **kwargs):
        """
        Enqueue the a function for execution.

        Parameters
        ----------
        func : callable
            Function which will be enqueued.

        \*args, \*\*kwargs :
            Arguments and keyword arguments passed to the function.

        Returns
        -------
        loading_page : str (html)
            The client's loading page.
        """
        return current_app.task_queue.enqueue(
            'flask_worker.tasks.execute_func',
            kwargs=dict(
                app_import=self.manager.app_import,
                worker_cls=type(self), 
                worker_id=inspect(self).identity[0],
                func=func, args=args, kwargs=kwargs
            )
        )
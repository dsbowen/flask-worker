"""# Routers"""

from flask import current_app
from sqlalchemy import Column, String
from sqlalchemy_mutable import MutableListType, MutableDictType

def set_route(func):
    """
    The `@set_route` decorator bookmarks the current function call. 
    Specifically, it sets the Router's `current_route` to the name of the 
    current function and stores the args and kwargs.
    """
    def with_route_setting(router, *args, **kwargs):
        router.current_route = func.__name__
        router.args = list(args)
        router.kwargs = kwargs
        return func(router, *args, **kwargs)
    return with_route_setting


class RouterMixin():
    """
    Mixin for router models. A router manages a series of function calls initiated by a view function. Among this series of function calls is the employer's complex task.

    Suppose a view function initiates a series of function calls which 
    include running a Worker. A Router allows the series of function calls to 
    'pause' while the Worker is running. Once the Worker finishes its job, 
    the Router resumes the series of function calls without repeating earlier 
    functions.

    Parameters
    ----------
    \*args, \*\*kwargs : 
        Passed to `super().__init__`.

    Attributes
    ----------
    current_route : str
        Name of the current 'route'. A route is one of the router's methods.

    args : list, default=[]
        Arguments for the current route, set from the `*args` parameter.

    kwargs : dict, default={}
        Keyword arguments for the current route, set from the `**kwargs` 
        parameter.
    """
    current_route = Column(String)
    args = Column(MutableListType)
    kwargs = Column(MutableDictType)

    def __init__(self, *args, **kwargs):
        self.args = self.args or []
        self.kwargs = self.kwargs or {}
        super().__init__(*args, **kwargs)

    def route(self):
        """
        Route the request to the `current_route`.

        Returns
        -------
        page_html : str
            Html of the page returned by the current route.
        """
        page_html = getattr(self, self.current_route)(
            *self.args, **self.kwargs
        )
        current_app.extensions['manager'].db.session.commit()
        return page_html

    def run_worker(self, worker, next_route, *args, **kwargs):
        """
        Run a Worker, and return a call to the next route when finished.

        Parameters
        ----------
        worker : flask_worker.WorkerMixin
            Worker whose job should be run.

        next_route : callable
            The route which should be run after the worker has finished its 
            job.

        \*args, \*\*kwargs :
            Arguments and keyword arguments passed to `next_route`.

        Returns
        -------
        page_html : str
            Html of the page returned by the worker (if the job is not yet ]finished) or the next route function (after the job is finished).
        """
        return next_route(*args,**kwargs) if worker.job_finished else worker()
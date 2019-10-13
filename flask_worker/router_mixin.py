"""Router Mixin

The RouterMixin handles a series of functions called by a view function which include running a Worker.

Suppose a view function initiates a series of function calls which include running a Worker. A Router allows the series of function calls to 'pause' while the Worker is running. Once the Worker finishes its job, the Router resumes the series of function calls without repeating earlier functions.
"""

from flask import current_app
from sqlalchemy import Column, String
from sqlalchemy_mutable import MutableListType, MutableDictType

def set_route(func):
    """Create a 'bookmark' for the current function
    
    The @set_route decorator creates a 'bookmark' for the current function 
    call. Specifically, it sets the Router's `current_route` to the name of 
    the current function and stores the args and kwargs.
    """
    def with_route_setting(router, *args, **kwargs):
        router.current_route = func.__name__
        router.args = list(args)
        router.kwargs = kwargs
        return func(router, *args, **kwargs)
    return with_route_setting


class RouterMixin():
    current_route = Column(String)
    args = Column(MutableListType)
    kwargs = Column(MutableDictType)

    def __init__(self, *args, **kwargs):
        self.args = self.args or []
        self.kwargs = self.kwargs or {}
        super().__init__(*args, **kwargs)

    def route(self):
        """Route the request to the `current_route`"""
        page_html = getattr(self, self.current_route)(
            *self.args, **self.kwargs
        )
        db = current_app.extensions['manager'].db
        db.session.commit()
        return page_html

    def run_worker(self, worker, next_route, args=[], kwargs={}):
        """Run a Worker
        
        Return a call to the `next_route` when finished.
        """
        if not worker.job_finished:
            return worker()
        return next_route(*args, **kwargs)
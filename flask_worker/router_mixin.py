"""Router Mixin"""

from flask import current_app
from sqlalchemy import Column, String
from sqlalchemy_mutable import MutableListType, MutableDictType

def set_route(func):
    """Set the function name as the current route"""
    def with_route_setting(router, *args, **kwargs):
        router.current_route = func.__name__
        router.args = list(args)
        router.kwargs = kwargs
        return func(router, *args, **kwargs)
    return with_route_setting


class RouterMixin():
    current_route = Column(String)
    args = Column(MutableListType, default=[])
    kwargs = Column(MutableDictType, default={})

    def route(self):
        current_route = self.current_route
        page_html = getattr(self, current_route)(
            *self.args, **self.kwargs
        )
        db = current_app.extensions['manager'].db
        db.session.commit()
        return page_html

    def run_worker(self, worker, next_route, args=[], kwargs={}):
        if worker.ready_to_work or worker.job_in_progress:
            return worker()
        return next_route(*args, **kwargs)
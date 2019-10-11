"""Router Mixin"""

from flask import current_app
from sqlalchemy import Column, String

def set_route(func):
    """Set the function name as the current route"""
    def with_route_setting(router):
        router.current_route = func.__name__
        return func(router)
    return with_route_setting


class RouterMixin():
    current_route = Column(String)
    default_route = Column(String)

    def route(self):
        current_route = self.current_route or self.default_route
        page_html = getattr(self, current_route)()
        db = current_app.extensions['manager'].db
        db.session.commit()
        return page_html

    def run_worker(self, worker, next_route):
        if worker.ready_to_work or worker.job_in_progress:
            return worker()
        return next_route()
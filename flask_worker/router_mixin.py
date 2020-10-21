"""# Routers"""

from flask import current_app
from sqlalchemy import Column, String
from sqlalchemy.inspection import inspect
from sqlalchemy_mutable import MutableType, partial as partial_base

from functools import wraps

def set_route(func):
    """
    The `@set_route` decorator bookmarks the current function call. 
    Specifically, it sets the Router's `func` to the the current function and 
    stores the args and kwargs.
    """
    @wraps(func)
    def with_route_setting(router, *args, **kwargs):
        router.func = partial(func, *args, **kwargs)
        return func(router, *args, **kwargs)
        
    return with_route_setting


class partial(partial_base):
    def __init__(self, func, *args, **kwargs):
        self.func = func.__name__
        self.args, self.kwargs = list(args), kwargs

    def __call__(self, router, *args, **kwargs):
        print('self func is', self.func)
        func = getattr(router, self.func)
        kwargs_ = self.kwargs.unshell()
        kwargs_.update(kwargs)
        return func(*args, *self.args.unshell(), **kwargs)


class RouterMixin():
    """
    Mixin for Router models. A Router manages a series of function calls 
    initiated by a view function. These function calls must be methods of the 
    Router.

    Suppose a view function initiates a series of function calls which include calling a Router. The Router can 'bookmark' its methods; if this Router is called in the future, it will pick up its series of function calls at the bookmarked method.

    Parameters
    ----------
    func : callable
        The function executed when the Router is called.

    \*args, \*\*kwargs : 
        Arguments and keyword arguments passed to `func`.

    Attributes
    ----------
    func : callable
        Set from the `func` parameter.

    init_func : callable
        Set from the `func` parameter. `func` is reset to `init_func` when the Router's `reset` method is called.
    """
    func = Column(MutableType)
    init_func = Column(MutableType)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.init_func = partial(func, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        """
        Calls `self.func`, passing in `self.args` and `self.kwargs`.

        Parameters
        ----------
        \*args, \*\*kwargs :
            Passed to the current function call.

        Returns
        -------
        page_html : str
            Html of the page returned by the current route.
        """
        func = self.func or self.init_func
        page_html = func(self, *args, **kwargs)
        session = current_app.extensions['manager'].db.session
        if not inspect(self).identity:
            session.add(self)
        session.commit()
        return page_html

    def reset(self):
        """
        Reset the series of function calls to its initial state.

        Returns
        -------
        self : flask_worker.RouterMixin
        """
        self.func = None
        return self
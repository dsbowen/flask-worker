"""# Routers"""

from flask import current_app
from sqlalchemy import Column, PickleType, String
from sqlalchemy.inspection import inspect
from sqlalchemy_function import FunctionMixin
from sqlalchemy_mutable import MutableListType, MutableDictType

from functools import wraps

def set_route(func):
    """
    The `@set_route` decorator bookmarks the current function call. 
    Specifically, it sets the Router's `func` to the the current function and 
    stores the args and kwargs.
    """
    @wraps(func)
    def with_route_setting(router, *args, **kwargs):
        router.set(func, *args, **kwargs)
        return func(router, *args, **kwargs)
    return with_route_setting


class RouterMixin(FunctionMixin):
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

    args : list, default=[]
        Set from the `*args` parameter.

    kwargs : dict, default={}
        Set from the `**kwargs` parameter.

    init_func : callable
        Set from the `func` parameter. `func` is reset to `init_func` when the Router's `reset` method is called.

    init_args : list, default=[]
        Set from the `*args` parameter. `args` is reset to `init_args` when the Router's `reset` method is called.

    init_kwargs : dict, default={}
        Similarly defined.
    """
    _func = Column(String)
    init_func = Column(PickleType)
    init_args = Column(MutableListType)
    init_kwargs = Column(MutableDictType)

    @property
    def func(self):
        return getattr(self, self._func)

    @func.setter
    def func(self, val):
        self._func = val.__name__

    def __init__(self, func, *args, **kwargs):
        self.init_func = func
        self.init_args, self.init_kwargs = list(args), kwargs
        super().__init__(func, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        """
        Calls `self.func`, passing in `self.args` and `self.kwargs`.

        Parameters
        ----------
        \*args, \*\*kwargs :
            Passed to `super().__call__`. See 
            <https://github.com/dsbowen/sqlalchemy-function/>.

        Returns
        -------
        page_html : str
            Html of the page returned by the current route.
        """
        page_html = super().__call__(*args, **kwargs)
        session = current_app.extensions['manager'].db.session
        if not inspect(self).identity:
            session.add(self)
        session.commit()
        return page_html

    def reset(self):
        """
        Reset `self.func`, `self.args`, and `self.kwargs` to their initial 
        values.

        Returns
        -------
        self : flask_worker.RouterMixin
        """
        self.set(self.init_func, *self.init_args, **self.init_kwargs)
        return self
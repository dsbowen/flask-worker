"""Tasks

This function is used by a Worker to execute its job (i.e. its 
Employer's complex task).

The worker's script connects a socket which listens for a 'job_finished' 
emission on a dedicated namespace for the worker (specified by the worker's 
`model_id`). When the socket hears the 'job_finished' emission, it replaces 
the worker's loading page with a request to the worker's `callback` view 
function.
"""

from pydoc import locate
import os
import sys

def execute_method(
    app_import, worker_cls, worker_id,
    model_cls, model_id, method_name, args, kwargs, 
):
    """
    Execute a database model's method. See `execute_method` in 
    `worker_mixin.py` for parameter details.
    """
    manager = JobManager().prepare_job(app_import, worker_cls, worker_id)
    model = model_cls.query.get(model_id)
    result = getattr(model, method_name)(*args, **kwargs)
    manager.finish_job()
    return result

def execute_func(app_import, worker_cls, worker_id, func, args, kwargs):
    """
    Execute a function. See `execute_function` in `worker_mixin.py` for 
    parameter details.
    """
    manager = JobManager().prepare_job(app_import, worker_cls, worker_id)
    result = func(*args, **kwargs)
    manager.finish_job()
    return result


class JobManager():
    def prepare_job(self, app_import, worker_cls, worker_id):
        # push the app context
        sys.path.insert(0, os.getcwd())
        app = locate(app_import)
        sys.path.pop(0)
        app.app_context().push()
        # get db and socketio
        manager = app.extensions['manager']
        self.db, self.socketio = manager.db, manager.socketio
        self.worker = worker_cls.query.get(worker_id)
        self.namespace = '/'+self.worker.model_id
        self.socketio.emit('job_started', namespace=self.namespace)
        return self

    def finish_job(self):
        self.worker.job_finished, self.worker.job_in_progress = True, False
        self.db.session.commit()
        self.socketio.emit('job_finished', namespace=self.namespace)
        return self
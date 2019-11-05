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

def execute(app_import, worker_class, worker_id):
    sys.path.insert(0, os.getcwd())
    app = locate(app_import)
    sys.path.pop(0)
    app.app_context().push()
    manager = app.extensions['manager']
    db, socketio = manager.db, manager.socketio
    worker = worker_class.query.get(worker_id)
    namespace = '/'+worker.model_id
    socketio.emit('job_started', namespace=namespace)
    result = worker.execute_job()
    db.session.commit()
    socketio.emit('job_finished', namespace=namespace)
    return result
"""Execute worker job"""

from flask import current_app

def execute(worker_class, worker_id):
    manager = current_app.extensions['manager']
    db, socketio = manager.db, manager.socketio
    worker = worker_class.query.get(worker_id)
    namespace = '/'+worker.model_id
    socketio.emit('job_started', namespace=namespace)
    result = worker.execute_job()
    db.session.commit()
    socketio.emit('job_finished', namespace=namespace)
    return result
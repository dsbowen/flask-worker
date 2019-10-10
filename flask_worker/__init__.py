from flask_worker.worker_mixin import WorkerMixin
from flask_worker.execute import execute

from flask import Blueprint, current_app, request
import rq

class Manager():
    def __init__(self, app=None, *args, **kwargs):
        self.connection = None
        self.db = None
        self.execute = 'tasks.execute_job'
        self.socketio = None

        self.setattrs(*args, **kwargs)
        if app is not None:
            self._init_app(app)
        
    def init_app(self, app, *args, **kwargs):
        self.setattrs(*args, **kwargs)
        self._init_app(app)

    def _init_app(self, app):
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['manager'] = self

        bp = Blueprint(
            'worker',
            __name__,
            template_folder='templates',
            static_url_path=app.static_url_path+'/flask_worker'
        )
        app.register_blueprint(bp)
        self.connection = self.connection or app.redis

        @app.route('/_check_job_status')
        def _check_job_status():
            job_id = request.args.get('job_id')
            connection = current_app.extensions['manager'].connection
            job = rq.job.Job.fetch(job_id, connection=connection)
            return {'job_finished': job.is_finished}
    
    def setattrs(
            self, connection=None, db=None, execute=None, socketio=None 
        ):
        self.connection = connection or self.connection
        self.db = db or self.db
        self.execute = execute or self.execute
        self.socketio = socketio or self.socketio
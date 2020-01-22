"""Flask-Worker

Flask-Worker simplifies interaction with a Redis Queue for executing 
long-running methods.

This file defines a Manager, which assists in managing workers. The manager 
tracks an application import path, a redis connection, the application 
database, and the web socket. These tools will be invoked by workers.
"""

from flask_worker.router_mixin import RouterMixin, set_route
from flask_worker.worker_mixin import WorkerMixin

from flask import Blueprint, current_app, request, url_for
import rq

from copy import copy

default_settings = {
    'app_import': 'app.app',
    'connection': None,
    'db': None,
    'loading_img_blueprint': None,
    'loading_img_filename': 'worker_loading.gif',
    'socketio': None,
    'template': 'worker/worker_loading.html',
}


class Manager():
    def __init__(self, app=None, **kwargs):
        settings = copy(default_settings)
        settings.update(kwargs)
        [setattr(self, key, val) for key, val in settings.items()]
        if app is not None:
            self._init_app(app)
        
    def init_app(self, app, **kwargs):
        [setattr(self, key, val) for key, val in kwargs.items()]
        self._init_app(app)

    def _init_app(self, app):
        """Initialize manager with application

        On app initialization, the manager defines a worker blueprint. The 
        worker blueprint template folder contains the worker script and 
        default html template. These can be found by flask.render_template.

        The constructor also defines the _check_job_status view function.
        """
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['manager'] = self

        bp = Blueprint(
            'worker',
            __name__,
            template_folder='templates'
        )
        app.register_blueprint(bp)
        self.connection = self.connection or app.redis

        @app.route('/_check_job_status')
        def _check_job_status():
            """Check job status

            This view function expects the worker's job id as a URL 
            parameter. It returns an indicator that the job has finished, 
            which will be interpreted as JSON by the worker script.

            It is called when the socket connects. This is because the 
            worker may complete its job, and emit the 'job_finished' 
            notification, before the socket connects. Without checking the 
            job status on socket connection, the loading page would not hear 
            the 'job_finished' emission and continue running indefinitely.
            """
            job_id = request.args.get('job_id')
            job = rq.job.Job.fetch(job_id, connection=self.connection)
            return {'job_finished': job.is_finished}

    @property
    def loading_img_src(self):
        try:
            bp = self.loading_img_blueprint
            static = bp + '.static' if bp else 'static'
            print(url_for(static, filename=self.loading_img_filename))
            return url_for(static, filename=self.loading_img_filename)
        except:
            return
"""# Manager"""

from flask_worker.router_mixin import RouterMixin, set_route
from flask_worker.worker_mixin import WorkerMixin

from flask import Blueprint, current_app, request, url_for
import rq

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
    """
    Flask extension which manages workers. The manager tracks an application 
    import path, a redis connection, the application database, and the web 
    socket. These tools will be invoked by workers.

    Parameters
    ----------
    app : flask.app.Flask or None, default=None
        Flask application for whose workers the manager is responsible. If the 
        app is passed to the contructor, the manager will be initialized with 
        the application. Otherwise, you must perform the initialization later 
        by calling `init_app`.

    \*\*kwargs :
        You can set the manager's attributes by passing them as keyword 
        arguments.    

    Attributes
    ----------
    app_import : str, default='app.app'
        Pythonic import path for the Flask application. e.g. if your 
        application object is created in a file `path/to/app.py` and named 
        `my_app`, set the `app_import` to `path.to.app.my_app`.

    connection : redis.client.Redis
        Redis connection for the workers. If not explicitly set, the manager 
        will set the connection attribute to the app's `redis` attribute. In 
        this case, the app must have a redis connection attribute named `redis` 
        when the manager is initialized with the application.

    db : flask_sqlalchemy.SQLAlchemy
       Database for the flask application.

    loading_img_blueprint : str or None, default=None
        Name of the blueprint to which the loading image belongs. If `None`, 
        the loading image is assumed to be in the app's `static` directory.

    loading_img_filename : str, default='worker_loading.gif'
        Name of the loading image file. This should be in the app's `static` 
        directory or a blueprint's `static` directory.

    loadering_img_src : str
        Loading image source path, derived from `loading_img_blueprint` and 
        `loading_img_filename`.

    socketio : flask_socketio.SocketIO or None, default=None
        Socket object through which workers will emit job progress messages. 
        While this argument is not required on initialization, it must be set 
        before the app is run.

    template : str, default='worker/worker_loading.html'
        Name of the html template file for the loading page. Flask-Worker 
        provides a default loading template.
    """
    def __init__(self, app=None, **kwargs):
        settings = default_settings.copy()
        settings.update(kwargs)
        [setattr(self, key, val) for key, val in settings.items()]
        if app is not None:
            self._init_app(app)
        
    def init_app(self, app, **kwargs):
        """
        Initialize the manager with the application.

        Parameters
        ----------
        app : flask.app.Flask
            Flask application for whose workers the manager is responsible.

        \*\*kwargs :
            You can set the manager's attributes by passing them as keyword 
            arguments.
        """
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
            return url_for(static, filename=self.loading_img_filename)
        except:
            pass
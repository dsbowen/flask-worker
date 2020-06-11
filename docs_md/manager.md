<script src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML" type="text/javascript"></script>

<link rel="stylesheet" href="https://assets.readthedocs.org/static/css/readthedocs-doc-embed.css" type="text/css" />

<style>
    a.src-href {
        float: right;
    }
    p.attr {
        margin-top: 0.5em;
        margin-left: 1em;
    }
    p.func-header {
        background-color: gainsboro;
        border-radius: 0.1em;
        padding: 0.5em;
        padding-left: 1em;
    }
    table.field-table {
        border-radius: 0.1em
    }
</style># Manager

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        
    </tbody>
</table>



##flask_worker.**Manager**

<p class="func-header">
    <i>class</i> flask_worker.<b>Manager</b>(<i>app=None, **kwargs</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/flask-worker/blob/master/flask_worker/__init__.py#L20">[source]</a>
</p>

Flask extension which manages workers. The manager tracks an application
import path, a redis connection, the application database, and the web
socket. These tools will be invoked by workers.

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>app : <i>flask.app.Flask or None, default=None</i></b>
<p class="attr">
    Flask application for whose workers the manager is responsible. If the app is passed to the contructor, the manager will be initialized with the application. Otherwise, you must perform the initialization later by calling <code>init_app</code>.
</p>
<b>**kwargs : <i></i></b>
<p class="attr">
    You can set the manager's attributes by passing them as keyword arguments.
</p></td>
</tr>
<tr class="field">
    <th class="field-name"><b>Attributes:</b></td>
    <td class="field-body" width="100%"><b>app_import : <i>str, default='app.app'</i></b>
<p class="attr">
    Pythonic import path for the Flask application. e.g. if your application object is created in a file <code>path/to/app.py</code> and named <code>my_app</code>, set the <code>app_import</code> to <code>path.to.app.my_app</code>.
</p>
<b>connection : <i>redis.client.Redis</i></b>
<p class="attr">
    Redis connection for the workers. If not explicitly set, the manager will set the connection attribute to the app's <code>redis</code> attribute. In this case, the app must have a redis connection attribute named <code>redis</code> when the manager is initialized with the application.
</p>
<b>db : <i>flask_sqlalchemy.SQLAlchemy</i></b>
<p class="attr">
    Database for the flask application.
</p>
<b>loading_img_blueprint : <i>str or None, default=None</i></b>
<p class="attr">
    Name of the blueprint to which the loading image belongs. If <code>None</code>, the loading image is assumed to be in the app's <code>static</code> directory.
</p>
<b>loading_img_filename : <i>str, default='worker_loading.gif'</i></b>
<p class="attr">
    Name of the loading image file. This should be in the app's <code>static</code> directory or a blueprint's <code>static</code> directory.
</p>
<b>loadering_img_src : <i>str</i></b>
<p class="attr">
    Loading image source path, derived from <code>loading_img_blueprint</code> and <code>loading_img_filename</code>.
</p>
<b>socketio : <i>flask_socketio.SocketIO or None, default=None</i></b>
<p class="attr">
    Socket object through which workers will emit job progress messages. While this argument is not required on initialization, it must be set before the app is run.
</p>
<b>template : <i>str, default='worker/worker_loading.html'</i></b>
<p class="attr">
    Name of the html template file for the loading page. Flask-Worker provides a default loading template.
</p></td>
</tr>
    </tbody>
</table>



####Methods



<p class="func-header">
    <i></i> <b>init_app</b>(<i>self, app, **kwargs</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/flask-worker/blob/master/flask_worker/__init__.py#L82">[source]</a>
</p>

Initialize the manager with the application.

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>app : <i>flask.app.Flask</i></b>
<p class="attr">
    Flask application for whose workers the manager is responsible.
</p>
<b>**kwargs : <i></i></b>
<p class="attr">
    You can set the manager's attributes by passing them as keyword arguments.
</p></td>
</tr>
    </tbody>
</table>


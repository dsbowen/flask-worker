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
</style># Workers

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        
    </tbody>
</table>



##flask_worker.**WorkerMixin**

<p class="func-header">
    <i>class</i> flask_worker.<b>WorkerMixin</b>(<i>template=None, **kwargs</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/flask-worker/blob/master/flask_worker/worker_mixin.py#L12">[source]</a>
</p>

The worker executes a complex task using a Redis queue. When called, it
enqueues a job and returns a loading page.

When a Redis worker grabs the enqueued job, it executes the worker's
function, `func`, passing in the worker's `args` and `kwargs`. After
execution, the worker's script replaces the client's window location with
a call to its `callback` view function.

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>template : <i>str or None, default=None</i></b>
<p class="attr">
    Name of the html template file for the worker's loading page. If <code>None</code>, the worker will use the manager's loading page template.
</p>
<b>**kwargs : <i></i></b>
<p class="attr">
    You can set the worker's attributes by passing them as keyword arguments.
</p></td>
</tr>
<tr class="field">
    <th class="field-name"><b>Attributes:</b></td>
    <td class="field-body" width="100%"><b>manager : <i>flask_worker.Manager</i></b>
<p class="attr">
    The worker's manager.
</p>
<b>func : <i>callable</i></b>
<p class="attr">
    Function which the worker will execute.
</p>
<b>args : <i>list, default=[]</i></b>
<p class="attr">
    Arguments which will be passed to the executed method.
</p>
<b>kwargs : <i>dict, default={}</i></b>
<p class="attr">
    Keyword arguments which will be passed to the executed method.
</p>
<b>callback : <i>str or None, default=None</i></b>
<p class="attr">
    Name of the view function to which the client will navigate once the worker has finished its job. If <code>None</code>, the current view function is re-called.
</p>
<b>job_finished : <i>bool, default=False</i></b>
<p class="attr">
    Indicates that the worker has finished its job.
</p>
<b>job_in_progress : <i>bool, default=False</i></b>
<p class="attr">
    Indicates that the worker has a job in progress.
</p>
<b>job_id : <i>str</i></b>
<p class="attr">
    Identifier for the worker's job.
</p>
<b>loading_page : <i>sqlalchemy_mutablesoup.MutableSoup</i></b>
<p class="attr">
    Loading page which will be displayed to the client while the worker performs its job.
</p>
<b>loading_img : <i>bs4.Tag</i></b>
<p class="attr">
    <code>&lt;img&gt;</code> tag for the loading image.
</p>
<b>loading_img_src : <i>str</i></b>
<p class="attr">
    Source of the loading image.
</p>
<b>result : <i></i></b>
<p class="attr">
    Output of the worker's function. This stores the result of the job the worker executed.
</p></td>
</tr>
    </tbody>
</table>



####Methods



<p class="func-header">
    <i></i> <b>reset</b>(<i>self</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/flask-worker/blob/master/flask_worker/worker_mixin.py#L105">[source]</a>
</p>

Clears the `job_finished`, `job_in_progress`, and `job_id` attributes.

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>self : <i>flask_worker.WorkerMixin</i></b>
<p class="attr">
    
</p></td>
</tr>
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>__call__</b>(<i>self</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/flask-worker/blob/master/flask_worker/worker_mixin.py#L117">[source]</a>
</p>

Enqueue the worker's job for execution if it is not enqueued already.

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>loading_page : <i>str (html)</i></b>
<p class="attr">
    The client's loading page.
</p></td>
</tr>
    </tbody>
</table>


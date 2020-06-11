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
</style># Routers

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        
    </tbody>
</table>



##flask_worker.**set_route**

<p class="func-header">
    <i>def</i> flask_worker.<b>set_route</b>(<i>func</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/flask-worker/blob/master/flask_worker/router_mixin.py#L7">[source]</a>
</p>

The `@set_route` decorator bookmarks the current function call.
Specifically, it sets the Router's `current_route` to the name of the
current function and stores the args and kwargs.

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        
    </tbody>
</table>



##flask_worker.**RouterMixin**

<p class="func-header">
    <i>class</i> flask_worker.<b>RouterMixin</b>(<i>*args, **kwargs</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/flask-worker/blob/master/flask_worker/router_mixin.py#L21">[source]</a>
</p>

Mixin for router models. A router manages a series of function calls initiated by a view function. Among this series of function calls is the employer's complex task.

Suppose a view function initiates a series of function calls which
include running a Worker. A Router allows the series of function calls to
'pause' while the Worker is running. Once the Worker finishes its job,
the Router resumes the series of function calls without repeating earlier
functions.

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>*args, **kwargs : <i></i></b>
<p class="attr">
    Passed to <code>super().__init__</code>.
</p></td>
</tr>
<tr class="field">
    <th class="field-name"><b>Attributes:</b></td>
    <td class="field-body" width="100%"><b>current_route : <i>str</i></b>
<p class="attr">
    Name of the current 'route'. A route is one of the router's methods.
</p>
<b>args : <i>list, default=[]</i></b>
<p class="attr">
    Arguments for the current route, set from the <code>*args</code> parameter.
</p>
<b>kwargs : <i>dict, default={}</i></b>
<p class="attr">
    Keyword arguments for the current route, set from the <code>**kwargs</code> parameter.
</p></td>
</tr>
    </tbody>
</table>



####Methods



<p class="func-header">
    <i></i> <b>route</b>(<i>self</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/flask-worker/blob/master/flask_worker/router_mixin.py#L57">[source]</a>
</p>

Route the request to the `current_route`.

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>page_html : <i>str</i></b>
<p class="attr">
    Html of the page returned by the current route.
</p></td>
</tr>
    </tbody>
</table>





<p class="func-header">
    <i></i> <b>run_worker</b>(<i>self, worker, next_route, *args, **kwargs</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/flask-worker/blob/master/flask_worker/router_mixin.py#L72">[source]</a>
</p>

Run a Worker, and return a call to the next route when finished.

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>worker : <i>flask_worker.WorkerMixin</i></b>
<p class="attr">
    Worker whose job should be run.
</p>
<b>next_route : <i>callable</i></b>
<p class="attr">
    The route which should be run after the worker has finished its job.
</p>
<b>*args, **kwargs : <i></i></b>
<p class="attr">
    Arguments and keyword arguments passed to <code>next_route</code>.
</p></td>
</tr>
<tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>page_html : <i>str</i></b>
<p class="attr">
    Html of the page returned by the worker (if the job is not yet ]finished) or the next route function (after the job is finished).
</p></td>
</tr>
    </tbody>
</table>


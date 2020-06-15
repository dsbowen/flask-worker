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
    <i>def</i> flask_worker.<b>set_route</b>(<i>func</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/flask-worker/blob/master/flask_worker/router_mixin.py#L9">[source]</a>
</p>

The `@set_route` decorator bookmarks the current function call.
Specifically, it sets the Router's `func` to the the current function and
stores the args and kwargs.

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        
    </tbody>
</table>



##flask_worker.**RouterMixin**

<p class="func-header">
    <i>class</i> flask_worker.<b>RouterMixin</b>(<i>func, *args, **kwargs</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/flask-worker/blob/master/flask_worker/router_mixin.py#L21">[source]</a>
</p>

Mixin for Router models. A Router manages a series of function calls
initiated by a view function. These function calls must be methods of the
Router.

Suppose a view function initiates a series of function calls which include calling a Router. The Router can 'bookmark' its methods; if this Router is called in the future, it will pick up its series of function calls at the bookmarked method.

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Parameters:</b></td>
    <td class="field-body" width="100%"><b>func : <i>callable</i></b>
<p class="attr">
    The function executed when the Router is called.
</p>
<b>*args, **kwargs : <i></i></b>
<p class="attr">
    Arguments and keyword arguments passed to <code>func</code>.
</p></td>
</tr>
<tr class="field">
    <th class="field-name"><b>Attributes:</b></td>
    <td class="field-body" width="100%"><b>func : <i>callable</i></b>
<p class="attr">
    Set from the <code>func</code> parameter.
</p>
<b>args : <i>list, default=[]</i></b>
<p class="attr">
    Set from the <code>*args</code> parameter.
</p>
<b>kwargs : <i>dict, default={}</i></b>
<p class="attr">
    Set from the <code>**kwargs</code> parameter.
</p>
<b>init_func : <i>callable</i></b>
<p class="attr">
    Set from the <code>func</code> parameter. <code>func</code> is reset to <code>init_func</code> when the Router's <code>reset</code> method is called.
</p>
<b>init_args : <i>list, default=[]</i></b>
<p class="attr">
    Set from the <code>*args</code> parameter. <code>args</code> is reset to <code>init_args</code> when the Router's <code>reset</code> method is called.
</p>
<b>init_kwargs : <i>dict, default={}</i></b>
<p class="attr">
    Similarly defined.
</p></td>
</tr>
    </tbody>
</table>



####Methods



<p class="func-header">
    <i></i> <b>__call__</b>(<i>self</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/flask-worker/blob/master/flask_worker/router_mixin.py#L75">[source]</a>
</p>

Calls `self.func`, passing in `self.args` and `self.kwargs`.

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
    <i></i> <b>reset</b>(<i>self</i>) <a class="src-href" target="_blank" href="https://github.com/dsbowen/flask-worker/blob/master/flask_worker/router_mixin.py#L91">[source]</a>
</p>

Reset `self.func`, `self.args`, and `self.kwargs` to their initial
values.

<table class="docutils field-list field-table" frame="void" rules="none">
    <col class="field-name" />
    <col class="field-body" />
    <tbody valign="top">
        <tr class="field">
    <th class="field-name"><b>Returns:</b></td>
    <td class="field-body" width="100%"><b>self : <i>flask_worker.RouterMixin</i></b>
<p class="attr">
    
</p></td>
</tr>
    </tbody>
</table>


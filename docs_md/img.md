# Loading image

The worker's loading page displays an image while waiting for its complex task to finish. Flask-Worker looks for a loading image named `worker_loading.gif` in the app's `static` directory.

Our folder looks like:

```
static/
    worker_loading.gif
factory.py
models.py
```

See the [API](manager.md) for details on customizing the loading page.
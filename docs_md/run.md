# Running the app

Make sure you have two terminal windows open, and navigate to your root directory in both.

## Running Redis

In one terminal window, we'll run the [Redis Queue](https://python-rq.org/).

```
$ rq worker my-task-queue
```

In your window, you should see a message like:

```
15:46:03: Worker rq:worker:e9f2ed95fc3e48429fc3962fe0f0c03b: started, version 1.2.0
15:46:03: *** Listening on my-task-queue...
15:46:03: Cleaning registries for queue: my-task-queue
```

Note that you can change the name of the task queue in the [application factory](factory.md).

## Running the app

In the other terminal window, we'll run the Flask app.

```
$ python app.py
```

In your window, you should see a message like:

```
15:54:51: Server initialized for eventlet.
15:54:51:  * Restarting with stat
15:54:52: Server initialized for eventlet.
15:54:52:  * Debugger is active!
15:54:52:  * Debugger PIN: 183-643-336
(3516) wsgi starting up on http://127.0.0.1:5000
```

## Viewing the app

Navigate to <http://localhost:5000> in your browser. Notice the following message in your redis terminal:

```
Complex task started
Progress: 0.0%
Progress: 20.0%
Progress: 40.0%
Progress: 60.0%
Progress: 80.0%
Progress: 100.0%
Complex task finished
```

While the complex task is executing, you'll see the loading gif in your browser. After the worker has finished, the page will reload with a 'Hello, World!' message.
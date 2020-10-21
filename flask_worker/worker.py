from flask import current_app, render_template, request
from sqlalchemy_mutable import partial

from random import choice, choices
from string import ascii_letters, digits

def _gen_id():
    return (
        choice(ascii_letters) 
        + ''.join(choices(ascii_letters+digits, k=90))
    )

class Worker(partial):
    @property
    def callback(self):
        if self._callback:
            return self._callback
        try:
            # if operating in request context
            return request.url
        except:
            # operating outside request context
            return self._callback

    @callback.setter
    def callback(self, val):
        self._callback = val

    @property
    def manager(self):
        return current_app.extensions['manager']

    def __init__(
            self, parent, func, args=(), kwargs={}, 
            callback=None, template=None, loading_img_src=None
        ):
        super().__init__(func, *args, **kwargs)
        self.parent = parent
        self.callback = callback
        self.template = template or self.manager.template
        self.loading_img_src = loading_img_src or self.manager.loading_img_src
        self.id = _gen_id()
        self.reset()

    def reset(self):
        self.job_finished, self.job_in_progress = False, False
        self.job_id = None
        return self

    def __call__(self):
        if not self.job_in_progress:
            self._enqueue()
        return render_template(self.template, worker=self)

    def _enqueue(self):
        job = current_app.task_queue.enqueue(
            'flask_worker.tasks.execute', 
            kwargs=dict(
                app_import=self.manager.app_import,
                parent=self.parent,
                worker=self
            )
        )
        self.job_finished, self.job_in_progress = False, True
        self.job_id = job.get_id()

    def _execute_job(self, *args, **kwargs):
        print('executing job')
        self.result = super().__call__(*args, **kwargs)
        self.job_finished, self.job_in_progress = True, False
        return self.result
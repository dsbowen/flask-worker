from app import app

from flask_worker import execute

app.app_context().push()

def execute_job(**kwargs):
    return execute(**kwargs)
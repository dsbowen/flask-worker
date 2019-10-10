from flask_worker import Manager

from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from redis import Redis
from rq import Queue
import eventlet
import os

db = SQLAlchemy()
eventlet.monkey_patch(socket=True)
socketio = SocketIO(asynch_mode='eventlet')
manager = Manager(db=db, socketio=socketio)

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'sqlite:///'+os.path.join(os.getcwd(), 'data.db')
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['EXPLAIN_TEMPLATE_LOADING'] = True
    app.redis = Redis.from_url('redis://')
    app.task_queue = Queue('my-task-queue', connection=app.redis)
    db.init_app(app)
    socketio.init_app(app, message_queue='redis://')
    manager.init_app(app)
    return app
#!/usr/bin/python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from flask import Flask
from flask import render_template,make_response,jsonify
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from zbxClient import ZbxClient
from celery import Celery

import sys
reload(sys)
sys.setdefaultencoding('utf8')

"""
celery install and cmd:
# pip install -U Celery
# celery worker -l INFO -A manage.celery

"""

from celery import platforms  #如果你不是linux的root用户，这两行没必要
platforms.C_FORCE_ROOT=True   #允许root权限运行celery

app = Flask(__name__)
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = "login"
login_manager.init_app(app)


def make_celery(app):
    celery = Celery("manage",  # 此处官网使用app.import_name，因为这里将所有代码写在同一个文件flask_celery.py,所以直接写名字。
                    broker=app.config['CELERY_BROKER_URL'],
                    backend=app.config['CELERY_RESULT_BACKEND']
                    )
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery

app.config.update(
    CELERY_BROKER_URL='redis://127.0.0.1:6379/0',
    CELERY_RESULT_BACKEND='redis://127.0.0.1:6379/1'
)

celery = make_celery(app)

@app.route("/")
def index():
    return render_template('dashboard.html')


@celery.task(bind = True)
def get_from_zabserver(self):
    client = ZbxClient()
    self.update_state(state='PROGRESS', meta={'i': 50})
    struct_data_list = client.getStructDatas()
    return {'result': struct_data_list}


@app.route('/run')
def run_work():
    # 长时间任务
    task = get_from_zabserver.apply_async()
    return jsonify({}),202,{'task_id':task.id}


@app.route('/status/<task_id>')
def get_task_status(task_id):
    the_task = get_from_zabserver.AsyncResult(task_id)
    print("任务：{0} 当前的 state 为：{1}".format(task_id, the_task.state))
    if the_task.state == 'PROGRESS':
        resp = {'state': 'progress', 'progress': 50, 'data': ''}
    elif the_task.state == 'SUCCESS':
        if 'result' in the_task.info:
            resp = {'state': "success",'progress': 100, 'data': the_task.info['result']}
    elif the_task.state == 'PENDING':   # 任务处于排队之中
        resp = {'state': 'waitting', 'progress': 0, 'data': ''}
    else:
        if 'result' in the_task.info:
            resp = {'state': "success", 'progress': 100,'data': the_task.info['result']}
        else:
            resp = {'state': 'failure', 'progress': 0, 'data': ''}
    return jsonify(resp)


@app.errorhandler(400)
def internal_error(error):
    return make_response(jsonify({'message': {'status': "1", 'info': "Error request"}}), 400)

@app.errorhandler(404)
def not_find(error):
    return render_template('404.html'),404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'),500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=True)

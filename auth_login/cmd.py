#!/usr/bin/env python
#coding: utf-8
#@author flftuu
#@mail   flftuu@teamsun.com.cn

from gevent import monkey
monkey.patch_all()

from flask import Flask, request, abort, render_template
from werkzeug.exceptions import BadRequest
import gevent

from common import get_wsgi_args
import auth_login


import server

## 设置网络应用app

## Flask 轻量级的wsgi 服务器
app = Flask(__name__)


## 设置 首页
@app.route('/')
def index():
    ## 项目目录中 必须有 templates 目录 并且里面有 index.html 文件
    return render_template('index.html')

## 设置 登入页
@app.route('/wssh/<hostname>/<username>')
def connect(hostname,username):
    app.logger.debug('{remote} -> {username}@{hostname}: {command}'.format(
        remote=request.remote_addr,
        username=username,
        hostname=hostname,
        command=request.args['run'] if 'run' in request.args else
        '[interactive shell]'
    ))
    
    ## 如果不是 一个 request 请求 则 报错
    # Abort if this is not a websocket request
    if not request.environ.get('wsgi.websocket'):
        app.logger.error('Abort: Request is not WebSocket upgradable')
        raise BadRequest()

    bridge = server.WSSHBridge(request.environ['wsgi.websocket'])

    try:
        bridge.open(
            hostname=hostname,
            username=username,
            password=request.args.get('password'),
            port=int(request.args.get('port')),
            private_key=request.args.get('private_key'),
            key_passphrase=request.args.get('key_passphrase'),
            allow_agent=app.config.get('WSSH_ALLOW_SSH_AGENT', False))
    except Exception as e:
        app.logger.exception('Error while connecting to {0}: {1}'.format(
            hostname, e.message))
        request.environ['wsgi.websocket'].close()
        return str()
    if 'run' in request.args:
        bridge.execute(request.args)
    else:
        bridge.shell()

    # We have to manually close the websocket and return an empty response,
    # otherwise flask will complain about not returning a response and will
    # throw a 500 at our websocket client
    request.environ['wsgi.websocket'].close()
    return str()

if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    from geventwebsocket.handler import WebSocketHandler
    from jinja2 import FileSystemLoader
    import os

    root_path = os.path.dirname(auth_login.__file__)
    app.jinja_loader = FileSystemLoader(os.path.join(root_path, 'templates'))
    app.static_folder = os.path.join(root_path, 'static')

    args = get_wsgi_args()

    app.config['WSSH_ALLOW_SSH_AGENT'] = args.allow_agent

    agent = 'auth_login server /{0}'.format(auth_login.__version__)

    print '{0} running on {1}:{2}'.format(agent, args.host, args.port)

    app.debug = args.debug

    http_server = WSGIServer((args.host, args.port), app,
        log=args.wsgi_log,
        handler_class=WebSocketHandler)
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        pass



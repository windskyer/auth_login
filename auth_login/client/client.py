# -*- coding: utf-8 -*-
#author leidong

import sys, os
import platform
import struct
import termios
import fcntl
import signal
import errno
import tty
import select

try:
    import simplejson as json
except ImportError:
    import json

import websocket


## Set client Error class
class ClientError(Exception):
        pass

class Client(object):
    """ Client conn to SSH Bridge Server """
    
    ## Set windows rows cols size
    def _pty_size(self, rows=24, cols=80):
        # Can't do much for Windows
        if platform.system() == 'Windows':
            return rows, cols

        fmt = 'HH'
        buffer = struct.pack(fmt, 0, 0)
        result = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ,
                         buffer)
        rows, cols = struct.unpack(fmt, result)
        return rows, cols
     
    ## Set tty windows size
    def _resize(self,ws):
        rows, cols = self._pty_size()
        ws.send(json.dumps({'resize': {'width': cols, 'height': rows}}))

    ## Set client conn to server 
    def invoke_shell(self, endpoint):
        ssh = websocket.create_connection(endpoint)
        self._resize(ssh)

        oldtty = termios.tcgetattr(sys.stdin)
        old_handler = signal.getsignal(signal.SIGWINCH)

        def on_term_resize(signum, frame):
            self._resize(ssh)

        signal.signal(signal.SIGWINCH, on_term_resize)

        try:
            ## 设置 tty 为 raw 模式就是 没有回显 和输出格式
            tty.setraw(sys.stdin.fileno())
            
            ## 设置 tty 为  没有回显 模式  
            tty.setcbreak(sys.stdin.fileno())
            
            ## 设置 长度 和 宽度
            rows, cols = self._pty_size()

            ## 发送 修改 窗口大小 参数
            ssh.send(json.dumps({'resize': {'width': cols, 'height': rows}}))

            while True:
                try:
                    r, w, e = select.select([ssh.sock, sys.stdin], [], [])
                    if ssh.sock in r:
                        data = ssh.recv()
                        if not data:
                            break
                    message = json.loads(data)
                    if 'error' in message:
                        raise ClientError(message['error'])
                    sys.stdout.write(message['data'])
                    sys.stdout.flush()
                    if sys.stdin in r:
                        x = sys.stdin.read(1)
                        if len(x) == 0:
                            break
                    ssh.send(json.dumps({'data': x}))
                except (select.error, IOError) as e:
                    if e.args and e.args[0] == errno.EINTR:
                        pass
                    else:
                        raise

        except websocket.WebSocketException:
            raise
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)
            signal.signal(signal.SIGWINCH, old_handler)


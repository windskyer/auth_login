# -*- coding: utf-8 -*-
#author leidong

"""
ssh.agent

This module provides server capabilities of wssh
"""

import paramiko
from paramiko import PasswordRequiredException
from paramiko.dsskey import DSSKey
from paramiko.rsakey import RSAKey
from paramiko.ssh_exception import SSHException

class WSSHBridge(object):
    """ WebSocket to SSH Bridge Server """

    def __init__(self):
        """ Initialize a WSSH Bridge

        The websocket must be the one created by gevent-websocket
        """
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())
        self._tasks = []
    
    def open(self, hostname, port=22, username=None, password=None,
                    private_key=None, key_passphrase=None,
                    allow_agent=False, timeout=None):
        """ Open a connection to a remote SSH server

        In order to connect, either one of these credentials must be
        supplied:
            * Password
                Password-based authentication
            * Private Key
                Authenticate using SSH Keys.
                If the private key is encrypted, it will attempt to
                load it using the passphrase
            * Agent
                Authenticate using the *local* SSH agent. This is the
                one running alongside wsshd on the server side.
        """
        try:
            self._ssh.connect(
                hostname=hostname,
                port=port,
                username=username,
                password=password,
                timeout=timeout,
                allow_agent=allow_agent,
                look_for_keys=False)

        except Exception as e:
            raise


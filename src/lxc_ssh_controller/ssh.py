#! /usr/bin/env python3
import time
import os.path
import getpass
from functools import wraps

import paramiko


class SSHCommandException(Exception):
    def __init__(self, msg, status_code):
        super().__init__(msg)
        self.status_code = status_code


def circuit_breaker(fn=None, retry=5):
    """
    Try callable `retry` times.
    """
    def circuit_breaker_decorator(fn):
        @wraps(fn)
        def circuit_breaker_wrapper(*args, **kwargs):
            for i in range(retry - 1):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    time.sleep(1)

            return fn(*args, **kwargs)

        return circuit_breaker_wrapper

    if fn:
        return circuit_breaker_decorator(fn)

    return circuit_breaker_decorator


class SSH:
    def __init__(self, address):
        self.address = address
        self.ssh = self.__class__.ssh_to_server(address)
        self._last_stderr = ""

    @staticmethod
    def ssh_to_server(address):
        key_path = os.path.expanduser("~/.ssh/id_rsa")
        key = paramiko.RSAKey.from_private_key_file(key_path)

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_system_host_keys()

        @circuit_breaker
        def connect():
            ssh.connect(
                hostname=address,
                username=getpass.getuser(),
                pkey=key,
                allow_agent=False
            )

        connect()

        return ssh

    def execute(self, command, raise_err=True):
        print(command)

        _, out, err = self.ssh.exec_command(command)
        status_code = out.channel.recv_exit_status()

        err_data = err.read().strip()
        err_data = err_data.replace(
            b"stty: 'standard input': Inappropriate ioctl for device",
            b""
        )
        self._last_stderr = err_data.strip()

        if status_code != 0 and raise_err:
            raise SSHCommandException(err_data, status_code)
        else:
            return out.read()

        return out.read()

    def close(self):
        self.ssh.close()

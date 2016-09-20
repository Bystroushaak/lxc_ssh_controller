#! /usr/bin/env python3
import json
import time

from ssh import SSH


class ContainerException(Exception):
    pass


class ContainerController:
    def __init__(self, address="172.16.221.3"):
        self._running_containers = set()

        self.ssh = SSH(address)

    @staticmethod
    def parse_ipv4(data, ipv4_only=True, raise_if_not_found=True):
        if not data:
            raise ContainerException("Container not found.")

        data = data[0]
        networks = data.get("state", {}).get("network", {})

        if "lo" in networks:
            del networks["lo"]

        addresses = (
            x.get("addresses", [])
            for x in networks.values()
        )

        ips = [
            x.get("address")
            for x in sum(addresses, [])
            if ipv4_only and x.get("family") == "inet"
        ]

        if raise_if_not_found and not ips:
            raise ValueError("No IP address found!")

        if ips:
            return ips[0]

        return ips

    def get_ip(self, container_name):
        def get_ip():
            data = self.ssh.execute(
                "lxc list %s --format json" % container_name
            )

            return self.__class__.parse_ipv4(
                json.loads(data.decode("utf-8")),
                raise_if_not_found=False,
            )

        # circuit breaker - it takes some time to get the IP from DHCP
        for i in range(5):
            ip = get_ip()

            if ip:
                return ip

            time.sleep(1)

        raise ValueError("Can't find IP address!")

    def stop_and_delete(self, container_name):
        self.ssh.execute(
            "lxc delete '%s' --force" % container_name,
            raise_err=False
        )

        if self.ssh._last_stderr:
            print(self.ssh._last_stderr)

        if container_name in self._running_containers:
            self._running_containers.remove(container_name)

    def copy_and_run(self, container_name, newname):
        assert container_name != newname

        self.stop_and_delete(newname)

        self.ssh.execute("lxc copy '%s' '%s'" % (container_name, newname))
        self.ssh.execute("lxc start '%s'" % newname)

        self._running_containers.add(newname)

    def close(self):
        self.ssh.close()

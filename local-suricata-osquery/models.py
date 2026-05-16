from falkordb_orm import node, relationship
from typing import List, Optional

@node(labels=["IPAddress"])
class IPAddress:
    def __init__(self, ip: str):
        self.ip = ip

@node(labels=["Process"])
class Process:
    def __init__(self, pid: int, name: str, cmdline: Optional[str] = None):
        self.pid = pid
        self.name = name
        self.cmdline = cmdline

@node(labels=["Host"])
class Host:
    def __init__(self, host_identifier: str, hostname: Optional[str] = None):
        self.host_identifier = host_identifier
        self.hostname = hostname

@node(labels=["Hostname"])
class Hostname:
    def __init__(self, name: str):
        self.name = name

""" Kill Process Extension """

import os
from albertv0 import *

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Kill Process"
__version__ = "1.2"
__trigger__ = "kill "
__author__ = "Benedict Dudel, Manuel Schneider"
__dependencies__ = []

iconPath = iconLookup('process-stop')


def owner(pid):
    for line in open('/proc/%s/status' % pid):
        if line.startswith('Uid:'):
            return int(line.split()[1])  # UID


def handleQuery(query):
    if query.isTriggered:
        results = []
        uid = os.getuid()
        for dir_entry in os.scandir('/proc'):
            if dir_entry.name.isdigit() and dir_entry.stat().st_uid == uid:
                try:
                    proc_command = open(os.path.join(dir_entry.path, 'comm'), 'r').read().strip()
                    if query.string in proc_command:
                        proc_cmdline = open(os.path.join(dir_entry.path, 'cmdline'), 'r').read().strip().replace("\0", " ")
                        results.append(
                            Item(
                                id="kill_%s" % dir_entry.name,
                                icon=iconPath,
                                text=proc_command,
                                subtext=proc_cmdline,
                                completion=query.rawString,
                                actions=[
                                    FuncAction("Terminate", lambda pid=dir_entry.name: os.kill(pid, os.SIGTERM)),
                                    FuncAction("Kill", lambda pid=dir_entry.name: os.kill(pid, os.SIGKILL))
                                ]
                            )
                        )
                except IOError:  # TOCTOU dirs may disappear
                    continue
        return results

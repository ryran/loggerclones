#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Ryan Sawhill Aroha rsaw@redhat.com
# See https://github.com/ryran/b19scripts/ for latest version
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Modules from standard library
from __future__ import print_function
import argparse, logging, logging.handlers
from socket import SOCK_DGRAM, SOCK_STREAM
from sys import exit, stdin, stderr
from os import getuid
from pwd import getpwuid

# Set some globals
prog = 'logger.py'
versionNumber = '0.2.1'
versionDate = '2016/04/12'
description = "A simplistic python logger clone that reads input via stdin"
epilog = "{} v{} last mod {};".format(prog, versionNumber, versionDate)
epilog += "\nFor issues & questions, see: https://github.com/ryran/loggerclones/issues"
user = getpwuid(getuid()).pw_name

# Add missing syslog levels to python logger
logging.addLevelName(25, 'NOTICE')
logging.addLevelName(60, 'ALERT')
logging.addLevelName(70, 'EMERG')

# Customize logging.handlers.SysLogHandler.priority_map to include added levels
loggerSyslogHandlerPriorityMap = {
    'DEBUG': 'debug',
    'INFO': 'info',
    'NOTICE': 'notice',
    'WARNING': 'warning',
    'ERROR': 'error',
    'CRITICAL': 'critical',
    'ALERT': 'alert',
    'EMERG': 'emerg',
    }

# Build a dict to establish what integer to pass to Logger.log()
syslogPriorityToLoggerLevel = {
    'debug': 10,
    'info': 20,
    'notice': 25,
    'warning': 30,
    'warn': 30,
    'error': 40,
    'err': 40,
    'critical': 50,
    'crit': 50,
    'alert': 60,
    'emerg': 70,
    'panic': 70,
    }

class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter):
    """This custom formatter eliminates the duplicate metavar in help lines."""
    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            parts = []
            if action.nargs == 0:
                parts.extend(action.option_strings)
            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    parts.append('%s' % option_string)
                parts[-1] += ' %s'%args_string
            return ', '.join(parts)

def parse_cmdline():
    fmt = lambda prog: CustomFormatter(prog)
    p = argparse.ArgumentParser(
        prog=prog,
        description=description,
        add_help=True,
        epilog=epilog,
        formatter_class=fmt)
    p.add_argument('-p', '--priority', metavar='PRIO', dest='priostring', default='user.info', help="specify priority for given message")
    p.add_argument('-t', '--tag', default=user, help="add tag to given message")
    p.add_argument('-i', '--id', action='store_true', help="add process ID to tag")
    g1 = p.add_mutually_exclusive_group()
    g1.add_argument('-u', '--socket', default='/dev/log', help="write to local UNIX socket")
    g1.add_argument('-d', '--udp', action='store_true', help="log via UDP instead of UNIX socket")
    g1.add_argument('-T', '--tcp', action='store_true', help="log via TCP instead of UNIX socket")
    p.add_argument('-n', '--server', default='localhost', help="DNS/IP of syslog server to use with --udp or --tcp")
    p.add_argument('-P', '--port', type=int, default=514, help="port to use with --udp or --tcp")
    opts =  p.parse_args()
    try:
        opts.facility = opts.priostring.split('.')[0]
        logging.handlers.SysLogHandler.facility_names[opts.facility]
        opts.priority = opts.priostring.split('.')[1]
        logging.handlers.SysLogHandler.priority_names[opts.priority]
        opts.level = syslogPriorityToLoggerLevel[opts.priority]
    except:
        print("Improper 'priority' specified")
        print("Must be <facility>.<priority> as described in logger(1) man page\n")
        raise
    return opts

def main():
    opts = parse_cmdline()
    myLogger = logging.getLogger(opts.tag)
    myLogger.setLevel(logging.DEBUG)
    if opts.udp:
        myHandler = logging.handlers.SysLogHandler(address=(opts.server, opts.port), facility=opts.facility, socktype=SOCK_DGRAM)
    elif opts.tcp:
        myHandler = logging.handlers.SysLogHandler(address=(opts.server, opts.port), facility=opts.facility, socktype=SOCK_STREAM)
    else:
        myHandler = logging.handlers.SysLogHandler(address=opts.socket, facility=opts.facility)
    myHandler.priority_map = loggerSyslogHandlerPriorityMap
    if opts.id:
        myFormatter = logging.Formatter('%(name)s[%(process)s]: %(message)s')
    else:
        myFormatter = logging.Formatter('%(name)s: %(message)s')
    myHandler.setFormatter(myFormatter)
    myLogger.addHandler(myHandler)
    while 1:
        line = stdin.readline()
        if not line:
            break
        myLogger.log(opts.level, line)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nReceived KeyboardInterrupt. Exiting.")
        exit()

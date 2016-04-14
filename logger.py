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
from os import getuid, getppid
from pwd import getpwuid

# Set some globals
prog = 'logger.py'
versionNumber = '0.3.1'
versionDate = '2016/04/14'
description = "A python logger clone that reads input from stdin, cmdline, or files"
epilog = "{0} v{1} last mod {2};".format(prog, versionNumber, versionDate)
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
    # Instantiate ArgumentParser
    p = argparse.ArgumentParser(
        prog=prog,
        description=description,
        add_help=True,
        epilog=epilog,
        formatter_class=fmt)
    p.add_argument('-p', '--priority', metavar='PRIO', dest='priostring', default='user.info', help="specify priority for given message")
    p.add_argument('-t', '--tag', default=user, help="add tag to given message")
    # Only one of the ID options can be used
    g0 = p.add_mutually_exclusive_group()
    g0.add_argument('-i', '--pid', action='store_true', help="append {0} PID to tag".format(prog))
    # The --id option has an optional argument
    g0.add_argument('--id', nargs='?', const='', help="append arbitrary ID to tag or if no ID specified, use PID")
    g0.add_argument('--ppid', action='store_true', help="append {0} parent PID to tag".format(prog))
    # Only one of --socket/--udp/--tcp can be used
    g1 = p.add_mutually_exclusive_group()
    g1.add_argument('-u', '--socket', default='/dev/log', help="write to local UNIX socket")
    g1.add_argument('-d', '--udp', action='store_true', help="log via UDP instead of UNIX socket")
    g1.add_argument('-T', '--tcp', action='store_true', help="log via TCP instead of UNIX socket")
    p.add_argument('-n', '--server', default='localhost', help="DNS/IP of syslog server to use with --udp or --tcp")
    p.add_argument('-P', '--port', type=int, default=514, help="port to use with --udp or --tcp")
    p.add_argument('-f', '--file', type=argparse.FileType('r'), help="log each line of FILE as a separate message instead of reading stdin or specifying MESSAGE on cmdline")
    p.add_argument('-e', '--skip-empty', action='store_true', help="ignore empty lines when using --file")
    # Slurp all remaining arguments into MESSAGE, just like logger does
    p.add_argument('message', metavar='MESSAGE', nargs='*', help="log single MESSAGE and quit instead of reading stdin")
    opts =  p.parse_args()
    # If facility.priority isn't specified or if either doesn't exist, throw fatal error
    try:
        opts.facility = opts.priostring.split('.')[0]
        logging.handlers.SysLogHandler.facility_names[opts.facility]
        opts.priority = opts.priostring.split('.')[1]
        logging.handlers.SysLogHandler.priority_names[opts.priority]
        opts.level = syslogPriorityToLoggerLevel[opts.priority]
    except:
        print("{0}: [ERROR] Improper 'priority' specified".format(prog), file=stderr)
        print("{0}: Must be <facility>.<priority> as described in logger(1) man page\n".format(prog), file=stderr)
        raise
    # Print warning if both --file & cmdline message specified
    if opts.file and opts.message:
        print("{0}: [WARNING] --file <FILE> and <MESSAGE> are mutually-exclusive; ignoring <MESSAGE>".format(prog), file=stderr)
    return opts

def main():
    # Parse cmdline into opts namespace
    opts = parse_cmdline()
    # Might as well name logger based on tag
    myLogger = logging.getLogger(opts.tag)
    # Set threshold as low as possible
    myLogger.setLevel(logging.DEBUG)
    # Instantiate handler as udp or tcp or plain local syslog
    if opts.udp:
        myHandler = logging.handlers.SysLogHandler(address=(opts.server, opts.port), facility=opts.facility, socktype=SOCK_DGRAM)
    elif opts.tcp:
        myHandler = logging.handlers.SysLogHandler(address=(opts.server, opts.port), facility=opts.facility, socktype=SOCK_STREAM)
    else:
        myHandler = logging.handlers.SysLogHandler(address=opts.socket, facility=opts.facility)
    # Use custom priority_map
    myHandler.priority_map = loggerSyslogHandlerPriorityMap
    # Determine whether to print [ID] after tag
    if opts.pid or opts.id is not None:
        if opts.id:
            # Print TAG[CUSTOM_ID] (passed via --id=xxx)
            myFormatter = logging.Formatter('%(name)s[{0}]: %(message)s'.format(opts.id))
        else:
            # Print TAG[PID] (due to -i or --id)
            myFormatter = logging.Formatter('%(name)s[%(process)s]: %(message)s')
    elif opts.ppid:
        # Print TAG[PPID] (due to --ppid)
        myFormatter = logging.Formatter('%(name)s[{0}]: %(message)s'.format(getppid()))
    else:
        # Print just TAG
        myFormatter = logging.Formatter('%(name)s: %(message)s')
    # Add formatter to handler
    myHandler.setFormatter(myFormatter)
    # Add handler to logger
    myLogger.addHandler(myHandler)
    # What to log ...
    if opts.file:
        # If passed a file, log each line from file
        for line in opts.file:
            if opts.skip_empty and not line.strip():
                continue
            myLogger.log(opts.level, line)
    elif opts.message:
        # If passed a message on the cmdline, log that instead
        myLogger.log(opts.level, " ".join(opts.message))
    else:
        # Otherwise, log each line of stdin until receive EOF (Ctrl-d)
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

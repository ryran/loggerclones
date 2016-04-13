# loggerclones
The nix logger command reimplemented in portable scripting languages without any legacy 1024-byte message-size restriction.

## [Python](https://github.com/ryran/loggerclones/blob/master/logger.py)
- Uses Python's standard [logging](https://docs.python.org/2/library/logging.html) module
- Differences with modern `logger` command:
  - Has no 1024-byte message-size restriction (no message splitting performed)
  - Supports new `--ppid` option to append *parent* process id to tag
  - Does not support `--stderr` option
- Similarities with modern `logger` command:
  - Accepts log message as command-line arguments
  - Accepts log messages via stdin
  - Accepts log messages by reading file passed to `-f` / `--file`
  - Single-letter opts and full-word opts are completely compatible
  - Supports specifying custom facility.priority
  - Supports sending to custom socket, local/remote tcp & udp
  - Supports custom tags
  - Supports adding PID to tag
  - Supports adding custom (arbitrary) ID to tag

##### Tested on
- Fedora
- RHEL 7
- RHEL 6 (install `python-argparse` package)

##### Help page

```
$ ./logger.py -h
usage: logger.py [-h] [-p PRIO] [-t TAG] [-i | --id [ID] | --ppid]
                 [-u SOCKET | -d | -T] [-n SERVER] [-P PORT] [-f FILE] [-e]
                 [MESSAGE [MESSAGE ...]]

A python logger clone that reads input from stdin, cmdline, or files

positional arguments:
  MESSAGE              log single MESSAGE and quit instead of reading stdin
                       (default: None)

optional arguments:
  -h, --help           show this help message and exit
  -p, --priority PRIO  specify priority for given message (default: user.info)
  -t, --tag TAG        add tag to given message (default: rsaw)
  -i, --pid            append logger.py PID to tag (default: False)
  --id [ID]            append arbitrary ID to tag or if no ID specified, use
                       PID (default: None)
  --ppid               append logger.py parent PID to tag (default: False)
  -u, --socket SOCKET  write to local UNIX socket (default: /dev/log)
  -d, --udp            log via UDP instead of UNIX socket (default: False)
  -T, --tcp            log via TCP instead of UNIX socket (default: False)
  -n, --server SERVER  DNS/IP of syslog server to use with --udp or --tcp
                       (default: localhost)
  -P, --port PORT      port to use with --udp or --tcp (default: 514)
  -f, --file FILE      log each line of FILE as a separate message instead of
                       reading stdin or specifying MESSAGE on cmdline
                       (default: None)
  -e, --skip-empty     ignore empty lines when using --file (default: False)

logger.py v0.3.0 last mod 2016/04/13; For issues & questions, see:
https://github.com/ryran/loggerclones/issues
```

## [Perl](https://github.com/ryran/loggerclones/blob/master/logger.pl)
- Uses Perl's standard [Sys::Syslog](http://perldoc.perl.org/Sys/Syslog.html) module
- Differences with modern `logger` command:
  - Has no 1024-byte message-size restriction (no message splitting performed)
  - Does not accept log message as command-line arguments
  - Does not support passing file via `-f` / `--file`
  - Does not support adding custom (arbitrary) ID to tag
- Similarities with modern `logger` command:
  - Accepts log messages via stdin
  - Single-letter opts and full-word opts are completely compatible
  - Supports specifying custom facility.priority
  - Supports sending to custom socket, local/remote tcp & udp
  - Supports custom tags
  - Supports adding PID to tag
  - Supports `--stderr` option

##### Tested on
- Fedora
- RHEL 7
- RHEL 6
- RHEL 5

##### Help page

```
$ ./logger.pl -h
usage: logger.pl [-h|--help] [-p PRIO] [-t TAG] [-i] [-u SOCKET | --udp | --tcp]
                 [-n SERVER] [-P PORT]

A perl logger clone that reads input via stdin

optional arguments:
  -h, --help           show this help message and exit
  -p, --priority PRIO  specify priority for given message (default: user.info)
  -t, --tag TAG        add tag to given message (default: rsaw)
  -i, --id             add process ID to tag (default: False)
  -u, --socket SOCKET  write to local UNIX socket (default: /dev/log)
  -d, --udp            log via UDP instead of UNIX socket (default: False)
  -T, --tcp            log via TCP instead of UNIX socket (default: False)
  -n, --server SERVER  DNS/IP of syslog server to use with --udp or --tcp
                       (default: localhost)
  -P, --port PORT      port to use with --udp or --tcp (default: 514)
  -s, --stderr         output to standard error as well (default: False)

logger.pl v0.1.2 last mod 2016/04/12
For issues & questions, see: https://github.com/ryran/loggerclones/issues
```
# loggerclones
The nix logger command reimplemented in portable scripting languages without any legacy 1024-byte message-size restriction.

## [Python](https://github.com/ryran/loggerclones/logger.py)
Uses Python's standard [logging](https://docs.python.org/2/library/logging.html) module

##### Tested on
- Fedora
- RHEL 7
- RHEL 6 (install `python-argparse` package)

##### Help page

```
$ ./logger.py -h
usage: logger.py [-h] [-p PRIO] [-t TAG] [-i] [-u SOCKET | -d | -T]
                 [-n SERVER] [-P PORT]

A python logger clone that reads input via stdin

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

logger.py v0.2.1 last mod 2016/04/12; For issues & questions, see:
https://github.com/ryran/loggerclones/issues
```

## [Perl](https://github.com/ryran/loggerclones/logger.pl)
Uses Perl's standard [Sys::Syslog](http://perldoc.perl.org/Sys/Syslog.html) module

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
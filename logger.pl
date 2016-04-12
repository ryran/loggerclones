#!/usr/bin/perl
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

use strict;
# use warnings;
use Getopt::Long qw( GetOptions );
use Sys::Syslog qw( :DEFAULT setlogsock );

Getopt::Long::Configure ("gnu_getopt");

my $print_help;
my $tag = (getpwuid($<))[0];
my $prio_string = 'user.info';
my $facility = '';
my $priority = '';
my $socket = '/dev/log';
my $use_stderr;
my $use_pid;
my $use_tcp;
my $use_udp;
my $syslog_server= 'localhost';
my $port = 514;
my $openlog_opts = 'cons';
my $log;
my @facilities = qw( auth authpriv cron daemon ftp lpr mail news syslog user uucp local0 local1 local2 local3 local4 local5 local6 local7 );
my @priorities = qw( debug info notice warning warn err crit alert emerg panic );

sub get_usage {
    (my $usage = <<"    EOF") =~ s/^ {8}//gm;
        usage: logger.pl [-h|--help] [-p PRIO] [-t TAG] [-i] [-u SOCKET | --udp | --tcp]
                         [-n SERVER] [-P PORT]
    EOF
    return $usage;
}

sub get_help {
    (my $help = <<"    EOF") =~ s/^ {8}//gm;
        
        A perl logger clone that reads input via stdin
        
        optional arguments:
          -h, --help           show this help message and exit
          -p, --priority PRIO  specify priority for given message (default: $prio_string)
          -t, --tag TAG        add tag to given message (default: $tag)
          -i, --id             add process ID to tag (default: False)
          -u, --socket SOCKET  write to local UNIX socket (default: $socket)
          -d, --udp            log via UDP instead of UNIX socket (default: False)
          -T, --tcp            log via TCP instead of UNIX socket (default: False)
          -n, --server SERVER  DNS/IP of syslog server to use with --udp or --tcp
                               (default: $syslog_server)
          -P, --port PORT      port to use with --udp or --tcp (default: $port)
          -s, --stderr         output to standard error as well (default: False)
        
        logger.pl v0.1.2 last mod 2016/04/12
        For issues & questions, see: https://github.com/ryran/loggerclones/issues
    EOF
    return $help;
}

sub print_prio_err {
    print "Improper 'priority' specified\n";
    print "Must be <facility>.<priority> as described in logger(1) man page\n";
}

# Parse options
GetOptions(
    'help|h' => \$print_help,
    'tcp|T' => \$use_tcp,
    'udp|d' => \$use_udp,
    'id|i' => \$use_pid,
    'server|n=s' => \$syslog_server,
    'port|P=i' => \$port,
    'priority|p=s' => \$prio_string,
    'stderr|s' => \$use_stderr,
    'tag|t=s' => \$tag,
    'socket|u=s' => \$socket,
) or die get_usage();

# Check arguments
if (length $print_help) {
    print get_usage();
    print get_help();
    exit;
}
($facility, $priority) = split('\.', $prio_string);
if ($facility eq '' || $priority eq '') {
    print_prio_err();
    exit 1;
}
my %facilities_set;
@facilities_set{@facilities} = ();
my %priorities_set;
@priorities_set{@priorities} = ();
if (exists $facilities_set{$facility} && exists $priorities_set{$priority}) {
} else {
    print_prio_err();
    exit 1;
}
if (length $use_tcp && length $use_udp) {
    print "Can't use --tcp and --udp at the same time\n";
    exit 1;
}

# Setup log socket
if ($socket eq '/dev/log') {
} elsif (length $use_tcp) {
    setlogsock({ type => 'tcp', port => $port, host => $syslog_server });
} elsif (length $use_udp) {
    setlogsock({ type => 'udp', port => $port, host => $syslog_server });
} else {
    setlogsock({ type => 'unix', path => $socket });
}

# Setup openlog opts
if (length $use_pid) {
    $openlog_opts .= ',pid';
}
if (length $use_stderr) {
    $openlog_opts .= ',perror';
}

# Open connection and start reading stdin
openlog($tag, $openlog_opts, $facility);
while ($log = <STDIN>) {
    syslog($priority, $log);
}
closelog;

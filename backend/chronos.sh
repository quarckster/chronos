#!/bin/sh
#
# init script for chronos
#

### BEGIN INIT INFO
# Provides:          chronos
# Required-Start:    $remote_fs $syslog $network
# Required-Stop:     $remote_fs $syslog $network
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: init script for the Chronos
# Description:       We'll have to fill this out later...
### END INIT INFO

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
NAME=chronos
DAEMON=/home/pi/Desktop/Chronos/Chronos_main.py
PIDFILE=/var/run/$NAME.pid
# LOGFILE=/var/log/$NAME.log

. /lib/lsb/init-functions

test -f $DAEMON || exit 0

case "$1" in
    start)
        start-stop-daemon --start --pidfile $PIDFILE --make-pidfile --background --startas $DAEMON
        log_end_msg $?
        ;;
    stop)
        start-stop-daemon --stop --pidfile $PIDFILE
        log_end_msg $?
        rm -f $PIDFILE
        ;;
    restart)
        $0 stop
        $0 start
        ;;
    status)
        start-stop-daemon --status --pidfile $PIDFILE
        log_end_msg $?
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 2
        ;;
esac

exit 0
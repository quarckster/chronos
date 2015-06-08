#!/bin/bash

function deploy_new_version {
    echo 'Commenting cron job'
    crontab -l | sed '/Chronos/s!^!#!' | crontab -

    echo 'Killing old Chronos processes'
    process_list=`ps ax | grep Chronos | awk '{print $1}' | sed 's/^//' | tr '\n' ' '`
    kill $process_list

    if mv /home/pi/Desktop/Chronos /home/pi/Desktop/Chronos.old; then
        echo 'Current Chronos dir has moved to Chronos.old'
    else
        echo 'Moving current Chronos dir to Chronos.old failed'
        exit 1
    fi

    if mv /home/pi/Desktop/Chronos.new /home/pi/Desktop/Chronos; then
        echo 'New Chronos dir has moved to current'
    else
        echo 'Moving new Chronos dir to current failed'
        exit 1
    fi

    if mysqldump -uroot -pestrrado Chronos > /home/pi/Desktop/Chronos.old.sql; then
        echo 'Current Chronos db has dumped to Chronos.old.sql'
    else
        echo 'Dumping current Chronos db to Chronos.old.sql failed'
        exit 1
    fi

    if mysql -uroot -pestrrado Chronos < /home/pi/Desktop/Chronos.new.sql; then
        echo 'New Chronos dump has restored to current db'
    else
        echo 'Restoring new Chronos dump to current db failed'
        exit 1
    fi

    echo 'Starting chronos service'
    service chronos start

    echo 'Moving current www dir to www.old'
    mv /var/www /var/www.old

    echo 'Moving new www dir to current'
    mv /var/www.new /var/www
}

function deploy_old_version {
    echo 'Stopping chronos service'
    service chronos stop

    if mv /home/pi/Desktop/Chronos /home/pi/Desktop/Chronos.new; then
        echo 'Current Chronos dir has moved to Chronos.new'
    else
        echo 'Moving current Chronos dir to Chronos.new failed'
        exit 1
    fi

    if mv /home/pi/Desktop/Chronos.old /home/pi/Desktop/Chronos; then
        echo 'Old Chronos dir has moved to current'
    else
        echo 'Moving old Chronos dir to current failed'
        exit 1
    fi

    if mysqldump -uroot -pestrrado Chronos > /home/pi/Desktop/Chronos.new.sql; then
        echo 'Current Chronos db has dumped to Chronos.new.sql'
    else
        echo 'Dumping current Chronos db to Chronos.new.sql failed'
        exit 1
    fi

    if mysql -uroot -pestrrado Chronos < /home/pi/Desktop/Chronos.old.sql; then
        echo 'Old Chronos dump has restored to current db'
    else
        echo 'Restoring old Chronos dump to current db failed'
        exit 1
    fi

    echo 'Uncommenting Chronos cron job'
    crontab -l | sed '/Chronos/s!^#!!' | crontab -

    echo 'Moving current www dir to www.new'
    mv /var/www /var/www.new

    echo 'Moving old www dir to current'
    mv /var/www.old /var/www
}



if [ "$1" = 'old' ]; then
    deploy_old_version
elif [ "$1" = 'new' ]; then
    deploy_new_version
else
    echo 'Bad argument. Choose old or new.'
    exit 1
fi

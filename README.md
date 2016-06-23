# Chronos #
## README ##

### What is this repository for? ###

Chronos is a boiling/cooling water system working on Raspberry Pi. Chronos has a web interface to control the system and tracking for the state.

![Alt text](http://i.imgur.com/8II1ydG.png "A screenshot of the Chronos web interface")
### Summary of set up ###
#### Installation ####
To install the latest version Chronos from Bitbucket repo enter the following command:
`# pip install --process-dependency-links git+https://bitbucket.org/quarck/chronos.git`

To install a certain version from a tag, commit or branch enter this:
`# pip install --process-dependency-links git+https://bitbucket.org/quarck/chronos.git@commit|tag|branch`
#### Configuration ####

The config file is a json file which is stored in /home/pi/chronos_config.json
#### Dependencies ####

* Flask
* pyserial
* apscheduler
* pymodbus
* sqlalchemy
* websocket-client
* SimpleWebSocketServer
#### Database configuration ####

TODO
#### Deployment instructions ####

Ensure modbus is working otherwise the web interface doesn't load in winter mode.

www-data and pi users have to be added in dialout group for managing serial port via web interface.

`# usermod -a -G dialout www-data`

To work with shared log file www-data and pi users have to be added in one group.

1. Create a new group `loggroup`:

    `# addgroup loggroup`  

2. Make a directory where the logs will be stored:

    `$ mkdir /tmp/chronos_logs`  

3. Make the containing directory group-writable:

    `$ chgrp loggroup /tmp/chronos_logs`

    `$ chmod g+w /tmp/chronos_logs`  

4. Set the setgid bit on logdir. That makes new files in logdir always owned by the group. Otherwise, new files are owned by the creator's group:

    `# chmod g+s /tmp/chronos_logs`  

5. Ensure all logging users belong to `loggroup`:

    `# usermod -a -G loggroup pi`  

    `# usermod -a -G loggroup www-data`  

6. Ensure all writing processes have the right umask so they can make newly created files group-writable:

    `$ umask 0002`

Chronos has a daemon which controlled by the following command:

`# service chronos start|stop|restart`
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

www-data and pi users have to be added in dialout group for managing serial port via web interface.

`# usermod -a -G dialout www-data`

To work with shared log and access to the db file www-data and pi users have to be added in one group.
Installation script does all required actions.

#### Files locations ####

chronos log directory: `/var/log/chronos`

chronos database directory: `/home/pi/chronos_db`

chronos config path: `/etc/chronos_config.json`
#### Managing ####
Chronos has a daemon which controlled by the following command:

`# service chronos start|stop|restart`
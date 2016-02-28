# Chronos #
## README ##

### What is this repository for? ###

Chronos is a boiling/cooling water system working on Raspberry Pi. Chronos has a web interface to control the system and tracking for the state.

![Alt text](http://i.imgur.com/8II1ydG.png "A screenshot of the Chronos web interface")
### Summary of set up ###
#### Installation ####
To install the latest version Chronos from Bitbucket repo enter the following command:
`sudo pip install git+https://bitbucket.org/quarck/chronos.git`

To install certain version from tag, commit or branch enter this:
`sudo pip install git+https://bitbucket.org/quarck/chronos.git@commit|tag|branch`
#### Configuration ####

The config file is a json file which is stored in /home/pi/chronos_config.json
#### Dependencies ####

* Flask
* pyserial
* lxml
* mysqlclient
* pymodbus
* zmq
#### Database configuration ####

TODO
#### Deployment instructions ####

Ensure modbus is working otherwise the web interface doesn't load in winter mode.

Chronos has a daemon which controlled by the following command:

`sudo service chronos start|stop|restart`
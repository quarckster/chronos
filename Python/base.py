#!/usr/bin/python

import ConfigParser
import logging
import os
from urlparse import urlparse

LOG_FILENAME = '/home/pi/Desktop/Chronos/log_Chronos.out'

class Base:

    def __init__(self, config_name = None):


        self.chillerPin = [0 for i in xrange(4)]

        if config_name is not None:
            __parseConfigFile(config_name)
        else:
            __initDefaultValues()

	logging.basicConfig(filename=self.log_file,
                            level=self.log_level,
                            format='%(asctime)s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M')

	logging.info("Configuration done")


    def __parseConfigFile(config_name):
	config = ConfigParser.RawConfigParser()
	config.read(config_name)

	self.log_file = config.get('log', 'file')
	self.log_level = config.getint('log', 'level')


    def __initDefaultValues():
        #Chronos main
        self.boilerPin = 20

        self.chillerPin[0] = 26
        self.chillerPin[1] = 16
        self.chillerPin[2] = 19
        self.chillerPin[3] = 5

        self.valve1Pin = 6
        self.valve2Pin = 12

        self.CCT = 5                 #Chiller Cascade Time
        self.temp_thresh = 80.00     #Threshold for breather LED color selection
        self.led_breather = 22

        self.led_red = 22
        self.led_green = 23
        self.led_blue = 24
        self.log_file = LOG_FILENAME
        
        #Chronos sec
        LOG_FILENAME = '/home/pi/Desktop/Chronos/log_Chronos_sec.out'
        self.systemUp = "/var/www/systemUp.txt"
        self.mysql_host="localhost"
        self.mysql_user="root"
        self.mysql_passwd="estrrado"
        self.mysql_db="Chronos"

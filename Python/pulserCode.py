#!/usr/bin/env python2.7  

import RPi.GPIO as GPIO

pulserPin = 17
p = GPIO.PWM(pulserPin, 80)
p.start(0)


#!/usr/bin/env python2.7  

import time
import os
import smtplib
import RPi.GPIO as GPIO

led_red = 22
led_green = 23
led_blue = 24

GPIO.setmode(GPIO.BCM)  
GPIO.setwarnings(False)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)  
GPIO.setup(led_red, GPIO.OUT)  
GPIO.setup(led_green, GPIO.OUT)
GPIO.setup(led_blue, GPIO.OUT)
GPIO.output(led_red,True)
time.sleep(1)
GPIO.output(led_green,True)
time.sleep(1)
GPIO.output(led_blue,True)
time.sleep(1)
GPIO.output(led_red,False)
GPIO.output(led_green,False)
GPIO.output(led_blue,False)
time.sleep(1)
GPIO.output(led_green,True)
time.sleep(1)
GPIO.output(led_green,False)
time.sleep(1)
GPIO.output(led_blue,True)
time.sleep(1)
GPIO.output(led_blue,False)
time.sleep(1)


while(1):

  print "Waiting for falling edge on port 27"  
  try:  
    GPIO.wait_for_edge(27, GPIO.FALLING)
    GPIO.output(led_red,True)
    GPIO.output(led_blue,True)
    time.sleep(0.5)
    GPIO.wait_for_edge(27, GPIO.FALLING)
     
    if(GPIO.input(27)==1): 
       time.sleep(0.5)
       if(GPIO.input(27)==1): 
          time.sleep(0.5)
          if(GPIO.input(27)==1): 
             time.sleep(3)
             if(GPIO.input(27)==1): 
                print "\nLong press detected."
                flag = 2 
       else: 
           print "\nShort press detected."
           flag = 1
    else: 
        print "\nShort press detected."
        flag = 1
  except KeyboardInterrupt:  
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit  
#GPIO.cleanup()           # clean up GPIO on normal exit
  if (flag == 1):
     print "\n Sending email..."
     os.system("sudo python /home/pi/Desktop/Chronos/sendEmail2.py")
  elif (flag == 2):
     print "\n Shutting down now."
     os.system("sudo shutdown now")
  flag = 0
  time.sleep(0.3)
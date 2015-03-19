
#!/usr/bin/env python2.7  

import time
import os
import smtplib
import RPi.GPIO as GPIO

led_red = 22
led_green = 23
led_blue = 24
flag = 0
pulserPin = 17

GPIO.setmode(GPIO.BCM)  
GPIO.setwarnings(False)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)  
GPIO.setup(led_red, GPIO.OUT)  
GPIO.setup(led_green, GPIO.OUT)
GPIO.setup(led_blue, GPIO.OUT)
GPIO.setup(pulserPin, GPIO.OUT)
try:
   os.system("sudo kill $(ps aux | grep led_starter.py | awk '{print $2 }')")
except:
   print "killError"
p = GPIO.PWM(led_red, 80)
p.start(0)
count = 0
try:
    while (count<5):
        for dc in range(0, 101, 5):
            p.ChangeDutyCycle(dc)
            time.sleep(0.06)
        for dc in range(100, -1, -5):
            p.ChangeDutyCycle(dc)
            time.sleep(0.06)
        count = count + 1
except:
   print ""
p.stop()

GPIO.output(led_blue,True)
time.sleep(0.5)
GPIO.output(led_blue,False)
time.sleep(0.5)
GPIO.output(led_blue,True)
time.sleep(5)
GPIO.output(led_blue,False)
time.sleep(2)

p = GPIO.PWM(pulserPin, 50000)
p.start(60)

while(1):

#  print "Waiting for falling edge on port 27"  
  try:  
    GPIO.wait_for_edge(27, GPIO.FALLING)
    GPIO.output(led_red,True)
    GPIO.output(led_blue,True)
    time.sleep(0.5)
    int_count = 0
    while(int_count<=10):
       int_count = int_count + 1
       time.sleep(0.2)
       if(GPIO.input(27)==1):
          flag = 3
    
    if(flag==3): 
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
     GPIO.output(led_red, False)
     print "\n Sending email..."
     os.system("sudo python /home/pi/Desktop/Chronos/sendEmail3.py")
  elif (flag == 2):
     GPIO.output(led_blue, False)
     print "\n Shutting down now."
     os.system("sudo shutdown now")
  flag = 0
  time.sleep(0.3)
  GPIO.output(led_blue, False)
  GPIO.output(led_red,False)
  GPIO.output(led_green,False)
  

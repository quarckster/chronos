import RPi.GPIO as GPIO ## Import GPIO library
import time
#led1 = 15
#led2 = 12
#led3 = 11
#led4 = 18
#led5 = 13
#led6 = 22
#led7 = 26
#led8 = 16
led1 = 20
led2 = 26
led3 = 16
led4 = 19
led5 = 5
led6 = 6
led7 = 12
led8 = 13

GPIO.setmode(GPIO.BCM) ## Use board pin numbering
GPIO.setup(led1, GPIO.OUT) ## Setup GPIO Pin 7 to OUT
GPIO.setup(led2, GPIO.OUT)
GPIO.setup(led3, GPIO.OUT)
GPIO.setup(led4, GPIO.OUT)
GPIO.setup(led5, GPIO.OUT)
GPIO.setup(led6, GPIO.OUT)
GPIO.setup(led7, GPIO.OUT)
GPIO.setup(led8, GPIO.OUT)

while True:
    GPIO.output(led1,True)
    time.sleep(1)
    GPIO.output(led1,False)
    GPIO.output(led2,True)
    time.sleep(1)
    GPIO.output(led2,False)
    GPIO.output(led3,True)
    time.sleep(1)
    GPIO.output(led3,False)
    GPIO.output(led4,True)
    time.sleep(1)
    GPIO.output(led4,False)
    GPIO.output(led5,True)
    time.sleep(1)
    GPIO.output(led5,False)
    GPIO.output(led6,True)
    time.sleep(1)
    GPIO.output(led6,False)
    GPIO.output(led7,True)
    time.sleep(1)
    GPIO.output(led7,False)
    GPIO.output(led8,True)
    time.sleep(1)
    GPIO.output(led8,False)


GPIO.cleanup()

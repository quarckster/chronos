import RPi.GPIO as GPIO ## Import GPIO library
import time
led1 = 15
led2 = 12
led3 = 11
led4 = 18
led5 = 13
led6 = 22
led7 = 26
led8 = 16


GPIO.setmode(GPIO.BOARD) ## Use board pin numbering
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
    time.sleep(10)
    GPIO.output(led2,True)
    time.sleep(1)
    GPIO.output(led2,False)
    time.sleep(1)
    GPIO.output(led3,True)
    time.sleep(1)
    GPIO.output(led3,False)
    time.sleep(1)
    GPIO.output(led4,True)
    time.sleep(1)
    GPIO.output(led4,False)
    time.sleep(1)
    GPIO.output(led5,True)
    time.sleep(1)
    GPIO.output(led5,False)
    time.sleep(1)
    GPIO.output(led6,True)
    time.sleep(1)
    GPIO.output(led6,False)
    time.sleep(1)
    GPIO.output(led7,True)
    time.sleep(1)
    GPIO.output(led7,False)
    time.sleep(1)
    GPIO.output(led8,True)
    time.sleep(1)
    GPIO.output(led8,False)
    time.sleep(1)


GPIO.cleanup()

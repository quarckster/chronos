#!/usr/bin/python
#version 2.0
#UID CHRON001

import time
time.sleep(15)
print "Initializing Chronos v2.0... Please stand by."
# -----|| one-time stuff ||-----
import logging
LOG_FILENAME = '/home/pi/Desktop/Chronos/log_Chronos.out'
logging.basicConfig(filename=LOG_FILENAME,
                    level=logging.DEBUG,
                    )
import os
import glob
import MySQLdb
import RPi.GPIO as GPIO
import ctypes
import commands
import urllib2
import string
import sre
from time import strftime
timeStamp = (time.strftime("%Y-%m-%d ") + time.strftime("%H:%M:00"))
logging.debug('Starting script')
# -----variables-----
waterOutTemp = 00.00
returnTemp = 00.00
boilerStatus = 0
chiller1Status = 0
chiller2Status = 0
MO_B = 0
MO_C1 = 0
MO_C2 = 0
GPIO_change = 0
a=0
b=0
c=0
t1 = 0
t2 = 0
t3 = 0
error_T1 = 0
error_T2 = 0
error_GPIO = 0
error_Web = 0
error_DB = 0
freeSD = 0
freeDB = 0
mode = 0
powerMode = 0
temp_thresh = 80.00
led_breather = 22
breather_count = 0

# -----Set GPIO pins-----
boilerPin = 20
chiller1Pin = 26
chiller2Pin = 16
led_red = 22
led_green = 23
led_blue = 24
try:
    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(boilerPin, GPIO.OUT)
    GPIO.setup(chiller1Pin, GPIO.OUT)
    GPIO.setup(chiller2Pin, GPIO.OUT)
    GPIO.output(boilerPin, False)
    GPIO.output(chiller1Pin, False)
    GPIO.output(chiller2Pin, False)
    GPIO.setup(led_red, GPIO.OUT)  
    GPIO.setup(led_green, GPIO.OUT)
    GPIO.setup(led_blue, GPIO.OUT)
    GPIO.output(led_red, False)
    GPIO.output(led_green, False)
    GPIO.output(led_blue, False)
except:
    error_GPIO = 1
    print "ErrorGPIO"
    GPIO.output(led_red,True)
    time.sleep(0.7)
    GPIO.output(led_red,False)
    logging.debug(timeStamp)
    logging.debug('ErrorGPIO')

#-----temp sensors-----
sensorOutID = '28-00042d4367ff'
sensorInID = '28-00042c648eff'
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

#-----kill related programs-----
try:
   os.system("sudo kill $(ps aux | grep firmwareUpgrade.py | awk '{print $2 }')")
except:
   print "killError"
   GPIO.output(led_red,True)
   time.sleep(0.7)
   GPIO.output(led_red,False)
   logging.debug(timeStamp)
   logging.debug('killError')

try:
   os.system("sudo kill $(ps aux | grep Chronos_starter.py | awk '{print $2 }')")
except:
   print "killError2"
   GPIO.output(led_red,True)
   time.sleep(0.7)
   GPIO.output(led_red,False)
   logging.debug(timeStamp)
   logging.debug('killError2')

#-----reset DB values-----
try:
   conn = MySQLdb.connect(host="localhost",user="root",passwd="estrrado",db="Chronos")
   cur = conn.cursor()
   cmd_main = ("UPDATE mainTable SET boilerStatus=%s, chiller1Status=%s, chiller2Status=%s, MO_B=%s, MO_C1=%s, MO_C2=%s, powerMode=%s ORDER BY LID DESC LIMIT 1", (boilerStatus, chiller1Status, chiller2Status, MO_B, MO_C1, MO_C2, powerMode))
   cur.execute(*cmd_main)
   conn.commit()
   conn.close()
except:
   print 'Error while resetting DB values'
   logging.debug(timeStamp)
   logging.debug('Error while resetting DB values')
   GPIO.output(led_red,True)
   time.sleep(0.7)
   GPIO.output(led_red,False)
   conn.rollback()

try:
   conn = MySQLdb.connect(host="localhost",user="root",passwd="estrrado",db="Chronos")
   cur = conn.cursor()
   cmd_main = ("UPDATE actStream SET timeStamp=%s, status=%s", (timeStamp, boilerStatus))
   cur.execute(*cmd_main)
   conn.commit()
   conn.close()
except:
   print 'Error resetting DB values'
   logging.debug(timeStamp)
   logging.debug('Error resetting DB values')
   GPIO.output(led_red,True)
   time.sleep(0.7)
   GPIO.output(led_red,False)
   conn.rollback()
# -----|| one-time stuff ||-----


# -----|| The main stuff ||-----
print "Starting script..."

while 1:
   time.sleep(2)
   timeStamp = (time.strftime("%Y-%m-%d ") + time.strftime("%H:%M:%S"))
   
   # Check for shutdown, restart, etc
   if(powerMode != 0):
      if(powerMode == 10):   
         os.system("sudo reboot")
      elif(powerMode == 20):
         os.system("sudo shutdown now")
      elif (powerMode == 2):
         os.system("sudo python /home/pi/Desktop/Chronos/firmwareUpgrade.py")
         time.sleep(10);
      elif (powerMode == 7):
         os.system("sudo python /home/pi/Desktop/Chronos/Chronos_starter.py")
         time.sleep(10);

      
   #Check if MySQL service is running
   output = commands.getoutput('ps -A')
   if 'mysqld' in output:
      error_DB = 0
   else:
      error_DB = 1
      GPIO.output(led_red,True)
      time.sleep(0.7)
      GPIO.output(led_red,False)

      
#---Here lies the code to determine free space in SD card and DB (not used)---      
#   p=os.popen("df /")
#   line = p.readline()
#   line = p.readline()
#   a = line.split()[1:4]
#   freeSD = ((float(a[1])/float(a[0]))*100)

#   conn = MySQLdb.connect(host="localhost",user="root",passwd="estrrado",db="Chronos")
#   cur = conn.cursor()
#   sql = "SELECT SUM(data_length + index_length)/1024/1024, SUM(data_free)/1024/1024 FROM information_schema.TABLES WHERE table_schema = 'Chronos'"
#   cur.execute(sql)
#   results = cur.fetchall()
#   for row in results:
#      DBSize = row[0]
#      DBFree = row[1]
#   freeDB = ((float(DBSize)/float(DBFree))*100)



   # Read Temperature Sensors
   try:
      error_T1 = 1
      error_T2 = 1
      for sensors in range (2):
         base_dir = '/sys/bus/w1/devices/'
         device_folder = glob.glob(base_dir + '28*')[sensors]
         device_file = device_folder + '/w1_slave'
         device_file_ID = device_folder + '/name'
         def read_temp_raw():
            f = open(device_file, 'r')
            lines = f.readlines()
            f.close()
            return lines

         def read_ID():
            f = open(device_file_ID, 'r')
            lines = f.read(15)
            f.close()
            return lines

         def read_temp():
            lines = read_temp_raw()
            while lines[0].strip()[-3:] != 'YES':
               time.sleep(0.2)
               lines = read_temp_raw()
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
               temp_string = lines[1][equals_pos+2:]
               temp = float(temp_string) / 1000.0 # Divide by 1000 for proper decimal point
               temp = temp * 9.0 / 5.0 + 32.0 # Convert to degF
               temp = round(temp, 1) # Round temp to 2 decimal points
               return temp

         if sensors == 0:
            if(read_ID() == sensorOutID):
               waterOutTemp = read_temp()
               error_T2 = 0
            elif(read_ID() == sensorInID):
               returnTemp = read_temp()
               error_T1 = 0
         if sensors == 1:
            if(read_ID() == sensorOutID):
               waterOutTemp = read_temp()
               error_T2 = 0
            elif(read_ID() == sensorInID):
               returnTemp = read_temp()
               error_T1 = 0
   except:
      print "Temp sensor error"
      logging.debug(timeStamp)
      logging.debug('Temp sensor error')
      GPIO.output(led_red,True)
      time.sleep(0.7)
      GPIO.output(led_red,False)


   # Read values from DB
   try:
       if (waterOutTemp > temp_thresh):
          led_breather = led_red
       else :
          led_breather = led_blue 
       if(breather_count==0):     
          GPIO.output(led_breather,True)
          time.sleep(0.1)
          GPIO.output(led_breather,False)
          time.sleep(0.1)
          GPIO.output(led_breather,True)
          time.sleep(0.1)
          GPIO.output(led_breather,False)
          time.sleep(0.1)
          breather_count = breather_count + 1
       else:
           breather_count = 0
           
       conn = MySQLdb.connect(host="localhost",user="root",passwd="estrrado",db="Chronos")
       cur = conn.cursor()
       sql = "SELECT * FROM mainTable ORDER BY LID DESC LIMIT 1"
       cur.execute(sql)
       results = cur.fetchall()
       for row in results:
           boilerStatus = row[5]
           chiller1Status = row[6]
           chiller2Status = row[7]
           setPoint2 = row[9]
           parameterX = row[10]
           parameterY = row[11]
           parameterZ = row[12]
           t1 = row[13]
           t2 = row[14]
           t3 = row[15]
           MO_B = row[16]
           MO_C1 = row[17]
           MO_C2 = row[18]
           mode = row[19]
           powerMode = row[20]
           
       conn.close()       
   except:
       print "Error fetching data from DB"
       logging.debug(timeStamp)
       logging.debug('Error fetching data from DB')
       GPIO.output(led_red,True)
       time.sleep(0.7)
       GPIO.output(led_red,False)

   #Parsing windChill from wx.thomaslivestock.com
   error_Web = 0
   try:
       website = urllib2.urlopen('http://wx.thomaslivestock.com')
       website_html = website.read()
       matches = sre.findall('[\d\.-]+\xb0F', website_html)
       if (mode == 0):
          outTemp = matches[2]
       elif (mode == 1):
            outTemp = matches[0]
       outTemp = outTemp[:outTemp.find('\xb0')]
       outsideTemp = float(outTemp)
   except:
       print 'Unable to get data from website'
       print 'Reading previous value from DB'
       logging.debug(timeStamp)
       logging.debug('Unable to get data from website. Reading previous value from DB.')
       error_Web = 1
       GPIO.output(led_red,True)
       time.sleep(0.7)
       GPIO.output(led_red,False)
       try:
           conn = MySQLdb.connect(host="localhost",user="root",passwd="estrrado",db="Chronos")
           cur = conn.cursor()
           sql = "SELECT outsideTemp FROM mainTable ORDER BY LID DESC LIMIT 1"
           cur.execute(sql)
           results = cur.fetchall()
           outsideTemp = results[0][0]           
           conn.close()
             
       except:
           print 'Unable to get value from DB'
           print 'Reverting to default value of 65 deg F...'
           logging.debug(timeStamp)
           logging.debug('Unable to get value from DB. Reverting to default value of 65 deg F...')
           outsideTemp = 65.00
           conn.close()


   # Calculate setpoint from windChill
   try:
       windChill = int(outsideTemp)
       windChillFile = open("/home/pi/Desktop/Chronos/windChillAvg.txt","r")
       buf = windChillFile.read(3)
       index = buf.find(".")
       windChillAvg = int(buf[0:index])
   except:
       print "Unable to open file to read"
       logging.debug(timeStamp)
       logging.debug('Unable to open file to read')
   if(windChill < 11):
      setpoint2 = 100
   else:
      try:
         conn = MySQLdb.connect(host="localhost",user="root",passwd="estrrado",db="Chronos")
         cur = conn.cursor()
         sql = ("SELECT setPoint FROM SetpointLookup WHERE windChill = %s", (windChill))
         cur.execute(*sql)
         results = cur.fetchall()
         setpoint2 = results[0][0]

      except:
         try:
            conn = MySQLdb.connect(host="localhost",user="root",passwd="estrrado",db="Chronos")
            cur = conn.cursor()
            sql = ("SELECT setPoint FROM SetpointLookup WHERE windChill = %s", (windChill))
            cur.execute(*sql)
            results = cur.fetchall()
            setpoint2 = results[0][0]

         except:
            print "setpoint error"
            logging.debug(timeStamp)
            logging.debug('setpoint error')
            
   if(windChillAvg < 71):
      setpointOffset = 0
   else:
      try:
         conn = MySQLdb.connect(host="localhost",user="root",passwd="estrrado",db="Chronos")
         cur = conn.cursor()
         sql = ("SELECT setPointOffset FROM SetpointLookup WHERE avgWindChill = %s", (windChillAvg))
         cur.execute(*sql)
         results = cur.fetchall()
         setpointOffset = results[0][0]
      except:
         try:
            conn = MySQLdb.connect(host="localhost",user="root",passwd="estrrado",db="Chronos")
            cur = conn.cursor()
            sql = ("SELECT setPointOffset FROM SetpointLookup WHERE avgWindChill = %s", (windChillAvg))
            cur.execute(*sql)
            results = cur.fetchall()
            setpointOffset = results[0][0]
         except:
            setpointOffset = 0
            print "Set point error"
            logging.debug(timeStamp)
            logging.debug('Set point error')
   setPoint2 = setpoint2 - setpointOffset
          
   # Conditions Check
   if MO_B == 0 :
      if ((mode==0) & (returnTemp <= (setPoint2 + parameterX - t1))) :
         a = 1
      elif ((mode==0) & (returnTemp > (setPoint2 + parameterX + t1))):
         a = 0
      elif (mode==1):
         a = 0
   elif MO_B == 1 :
       a = 1
   elif MO_B == 2 :
       a = 0

   if MO_C1 == 0 :
      if ((mode==1) & ((setPoint2 + parameterY + t2) <= returnTemp)) :
         b = 1
      elif ((mode==1) & ((setPoint2 + parameterY - t2) > returnTemp)) :
         b = 0
      elif (mode==0):
         b = 0
   elif MO_C1 == 1 :
       b = 1
   elif MO_C1 == 2 :
       b = 0
       
   if MO_C2 == 0 :
      if ((mode==1) & ((setPoint2 + parameterZ + t3) <= returnTemp)) :
         c = 1
      elif ((mode==1) & ((setPoint2 + parameterZ - t3) > returnTemp)) :
         c = 0
      elif (mode==0):
         c = 0
   elif MO_C2 == 1 :
       c = 1
   elif MO_C2 == 2 :
       c = 0
   
   GPIO_change = 0
   boiler_change = 0
   chiller1_change = 0
   chiller2_change = 0
   if boilerStatus != a:
       boilerStatus = a
       boiler_change = 1
       GPIO_change = 1
   if chiller1Status != b:
       chiller1Status = b
       chiller1_change = 1
       GPIO_change = 1
   if chiller2Status != c:
       chiller2Status = c
       chiller2_change = 1
       GPIO_change = 1

   # GPIO control
   if boiler_change == 1 :
       if boilerStatus == 1 :
           GPIO.output(boilerPin,True)
           bTime = (time.strftime("%Y-%m-%d ") + time.strftime("%H:%M:%S"))
           bStatus = 1
       elif boilerStatus == 0 :
           GPIO.output(boilerPin,False)
           bTime = (time.strftime("%Y-%m-%d ") + time.strftime("%H:%M:%S"))
           bStatus = 0


   if chiller1_change == 1 :
       if chiller1Status == 1 :
           GPIO.output(chiller1Pin,True)
           c1Time = (time.strftime("%Y-%m-%d ") + time.strftime("%H:%M:%S"))
           c1Status = 1
       elif chiller1Status == 0 :
           GPIO.output(chiller1Pin,False)
           c1Time = (time.strftime("%Y-%m-%d ") + time.strftime("%H:%M:%S"))
           c1Status = 0


   if chiller2_change == 1 :
       if chiller2Status == 1 :
           GPIO.output(chiller2Pin,True)
           c2Time = (time.strftime("%Y-%m-%d ") + time.strftime("%H:%M:%S"))
           c2Status = 1
       elif chiller2Status == 0 :
           GPIO.output(chiller2Pin,False)
           c2Time = (time.strftime("%Y-%m-%d ") + time.strftime("%H:%M:%S"))
           c2Status = 0


   # Update Databases
   try:
      conn = MySQLdb.connect(host="localhost",user="root",passwd="estrrado",db="Chronos")
      cur = conn.cursor()
      cmd_main = ("UPDATE mainTable SET outsideTemp=%s, waterOutTemp=%s, returnTemp=%s, boilerStatus=%s, chiller1Status=%s, chiller2Status=%s, setPoint2=%s ORDER BY LID DESC LIMIT 1", (outsideTemp, waterOutTemp, returnTemp, boilerStatus, chiller1Status, chiller2Status, setPoint2))
      cur.execute(*cmd_main)
      conn.commit()
      conn.close()
   except:
      print 'Error updating mainTable'
      logging.debug(timeStamp)
      logging.debug('Error updating mainTable')
      conn.rollback()

   try:
      conn = MySQLdb.connect(host="localhost",user="root",passwd="estrrado",db="Chronos")
      cur = conn.cursor()
      cmd_main = ("UPDATE errTable SET err_T1=%s, err_T2=%s, err_Web=%s, err_GPIO=%s, err_DB=%s", (error_T1, error_T2, error_Web, error_GPIO, error_DB))
      cur.execute(*cmd_main)
      conn.commit()
      conn.close()
   except:
      print 'Error updating errTable'
      logging.debug(timeStamp)
      logging.debug('Error updating errTable')
      conn.rollback()
   
   errData = [error_T1, error_T2, error_DB, error_Web, error_GPIO, freeSD, freeDB]
   try:
       dataFile = open('/var/www/sysStatus.txt', 'w')
       for eachitem in errData:
           dataFile.write(str(eachitem)+'\n')
       dataFile.close()
   except:
       print "Error opening file to write"
       logging.debug(timeStamp)
       logging.debug('Error opening file to write')
   
   if GPIO_change == 1:
       try:
          conn = MySQLdb.connect(host="localhost",user="root",passwd="estrrado",db="Chronos")
          cur = conn.cursor()
          
          if boiler_change == 1:
             cmd_b = ("UPDATE actStream SET timeStamp=%s, status=%s WHERE TID=1", (bTime, bStatus))
             cur.execute(*cmd_b)
          
          if chiller1_change == 1:
             cmd_c1 = ("UPDATE actStream SET timeStamp=%s, status=%s WHERE TID=2", (c1Time, c1Status))
             cur.execute(*cmd_c1)
         
          if chiller2_change == 1:
             cmd_c2 = ("UPDATE actStream SET timeStamp=%s, status=%s WHERE TID=3", (c2Time, c2Status))
             cur.execute(*cmd_c2)
             
          conn.commit()
          conn.close()
       except:
          print 'Error updating actStream'
          logging.debug(timeStamp)
          logging.debug('Error updating actStream')
          conn.rollback()
   
GPIO.cleanup()

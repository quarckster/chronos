#!/usr/bin/python
#version 2.0
#UID CHRON003
#New logic incoming

import time
# time.sleep(15)
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
# from time import strftime
timeStamp = (time.strftime("%Y-%m-%d ") + time.strftime("%H:%M:00"))
logging.debug('Starting script')

# -----variables-----
waterOutTemp = 00.00    #Temp sensor values. Also, the values that they...
returnTemp = 00.00      #    ...fall back to if sensors are not available
boilerStatus = 0        #ON = 1, OFF = 0
valveStatus = 0
valveFlag = 0

windChillAvg = 0

MO_B = 0                #Manual overrides. AUTO = 0, ON = 1, OFF = 2
GPIO_change = 0
a=0
b=0
c=0
t1 = 0                  #Threshold parameters
t2 = 0
t3 = 0
error_T1 = 0            #Error flags
error_T2 = 0
error_GPIO = 0
error_Web = 0
error_DB = 0
mode = 0                #Winter/Summer mode selector (0 -> Winter, 1 -> Summer)
powerMode = 0
temp_thresh = 80.00     #Threshold for breather LED color selection
led_breather = 22
breather_count = 0
CCT = 5                 #Chiller Cascade Time
nCon = 0
nCmax = 0
prev_eff_sp = 0
cur_eff_sp = 0
setPoint2 = 00.00
startTime = time.time()
ctime = (time.strftime("%Y-%m-%d "), time.strftime("%H:%M:%S"))
cstatus = 0
windSpeed = 0.00
spMin = 40.00
spMax= 100.00

# --------Arrays---------
p = [i for i in xrange(4)]
chillerStatus = [0 for i in xrange(4)]
MO_C = [0 for i in xrange(4)]
b = [0 for i in xrange(4)]
chillerChange = [0 for i in xrange(4)]
chillerPin = [0 for i in xrange(4)]
cTime = [(time.strftime("%Y-%m-%d "), time.strftime("%H:%M:%S")) for i in xrange(4)]
cStatus = [0 for i in xrange(4)]
sortTime = [0 for i in xrange(4)]
sortGap = [0 for i in xrange(4)]

       
# -----Set GPIO pins-----
boilerPin = 20
chillerPin[0] = 26
chillerPin[1] = 16
chillerPin[2] = 19
chillerPin[3] = 5
valve1Pin = 6
valve2Pin = 12
led_red = 22
led_green = 23
led_blue = 24
try:
    # GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(boilerPin, GPIO.OUT)
    GPIO.setup(chillerPin[0], GPIO.OUT)
    GPIO.setup(chillerPin[1], GPIO.OUT)
    GPIO.setup(chillerPin[2], GPIO.OUT)
    GPIO.setup(chillerPin[3], GPIO.OUT)
    GPIO.setup(valve1Pin, GPIO.OUT)
    GPIO.setup(valve2Pin, GPIO.OUT)
    GPIO.output(boilerPin, False)
    GPIO.output(chillerPin[0], False)
    GPIO.output(chillerPin[1], False)
    GPIO.output(chillerPin[2], False)
    GPIO.output(chillerPin[3], False)
    GPIO.output(valve1Pin, False)
    GPIO.output(valve2Pin, False)
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
#sensorOutID = '28-00000677d162'
#sensorInID = '28-00000676e315'
# os.system('modprobe w1-gpio')
# os.system('modprobe w1-therm')

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

try:
    conn = MySQLdb.connect(host="localhost",user="raspberry",passwd="estrrado",db="Chronos")
except Exception, e:
    print "Cannot connect to DB,", str(e)
    time.sleep(5)
    try:
        conn = MySQLdb.connect(host="localhost",user="raspberry",passwd="estrrado",db="Chronos")
    except Exception, e:
        print "Cannot connect to DB,", str(e)
        raise

#-----reset DB values-----
try:
   cur = conn.cursor()
   cmd_main = ("UPDATE mainTable SET boilerStatus=%s, chiller1Status=%s, chiller2Status=%s, chiller3Status=%s, chiller4Status=%s, MO_B=%s, MO_C1=%s, MO_C2=%s, MO_C3=%s, MO_C4=%s, powerMode=%s ORDER BY LID DESC LIMIT 1", (boilerStatus, chillerStatus[0], chillerStatus[1], chillerStatus[2], chillerStatus[3], MO_B, MO_C[0], MO_C[1], MO_C[2], MO_C[3], powerMode))
   cur.execute(*cmd_main)
   conn.commit()
except:
   print 'Error while resetting DB values'
   logging.debug(timeStamp)
   logging.debug('Error while resetting DB values')
   GPIO.output(led_red,True)
   time.sleep(0.7)
   GPIO.output(led_red,False)
   conn.rollback()

try:
   cur = conn.cursor()
   cmd_main = ("UPDATE actStream SET timeStamp=%s, status=%s", (timeStamp, boilerStatus))
   cur.execute(*cmd_main)
   conn.commit()

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

   # Read Temperature Sensors
   try:
      error_T1 = 1
      error_T2 = 1
      for sensors in range (2):
         base_dir = '/home/pi/fake_sys/'
         device_folder = glob.glob(base_dir + '28*')[sensors]
         print device_folder
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
               print "SensorOutID is %s. Temp is %s" % (read_ID(), waterOutTemp)
               error_T2 = 0
            elif(read_ID() == sensorInID):
               returnTemp = read_temp()
               print "SensorInID is %s. Temp is %s" % (read_ID(), returnTemp)
               error_T1 = 0
         if sensors == 1:
            if(read_ID() == sensorOutID):
               waterOutTemp = read_temp()
               print "SensorOutID is %s. Temp is %s" % (read_ID(), waterOutTemp)
               error_T2 = 0
            elif(read_ID() == sensorInID):
               returnTemp = read_temp()
               print "SensorInID is %s. Temp is %s" % (read_ID(), returnTemp)
               error_T1 = 0
   except Exception, e:
      print "Temp sensor error:", str(e)
      logging.debug(timeStamp)
      logging.debug('Temp sensor error')
      GPIO.output(led_red,True)
      time.sleep(0.7)
      GPIO.output(led_red,False)
      cur = conn.cursor()
      sql = "SELECT returnTemp FROM mainTable ORDER BY LID DESC LIMIT 1"
      cur.execute(sql)
      results = cur.fetchall()
      returnTemp = results[0][0]           


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
           
       cur = conn.cursor()
       sql = "SELECT * FROM mainTable ORDER BY LID DESC LIMIT 1"
       cur.execute(sql)
       results = cur.fetchall()
       for row in results:
           boilerStatus = row[5]
           chillerStatus[0] = row[6]
           chillerStatus[1] = row[7]
           chillerStatus[2] = row[8]
           chillerStatus[3] = row[9]
           setPoint2 = row[10]
           parameterX = row[11]
           t1 = row[12]
           MO_B = row[13]
           MO_C[0] = row[14]
           MO_C[1] = row[15]
           MO_C[2] = row[16]
           MO_C[3] = row[17]
           mode = row[18]
           powerMode = row[19]
           CCT = row[20]
   except:
       print "Error fetching data from DB"
       logging.debug(timeStamp)
       logging.debug('Error fetching data from DB')
       GPIO.output(led_red,True)
       time.sleep(0.7)
       GPIO.output(led_red,False)

   CCT = CCT*60

   #Parsing windChill and windSpeed from wx.thomaslivestock.com
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
           cur = conn.cursor()
           sql = "SELECT outsideTemp FROM mainTable ORDER BY LID DESC LIMIT 1"
           cur.execute(sql)
           results = cur.fetchall()
           outsideTemp = results[0][0]
       except:
           print 'Unable to get value from DB'
           print 'Reverting to default value of 65 deg F...'
           logging.debug(timeStamp)
           logging.debug('Unable to get value from DB. Reverting to default value of 65 deg F...')
           outsideTemp = 65.00
   try:
       website = urllib2.urlopen('http://wx.thomaslivestock.com')
       website_html = website.read()
       matches = sre.findall('[\d\.-]+ mph', website_html)
       windSpeed = matches[0]
       windSpeed = windSpeed[:windSpeed.find(' ')]
       windSpeed = float(windSpeed)
   except:
       print 'Unable to get wind speed from website'
       print 'Reading previous value from DB'
       logging.debug(timeStamp)
       logging.debug('Unable to get wind speed from website. Reading previous value from DB.')
       try:
           cur = conn.cursor()
           sql = "SELECT windSpeed FROM mainTable ORDER BY LID DESC LIMIT 1"
           cur.execute(sql)
           results = cur.fetchall()
           windSpeed = results[0][0]           
             
       except:
           print 'Unable to get wind speed from DB'
           print 'Reverting to default value of 0 mph...'
           logging.debug(timeStamp)
           logging.debug('Unable to get wind speed from DB. Reverting to default value of 0 mph...')
           windSpeed = 0.00


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
      setPoint2 = 100
   else:
      try:
         cur = conn.cursor()
         sql = ("SELECT setPoint FROM SetpointLookup WHERE windChill = %s", (windChill))
         cur.execute(*sql)
         results = cur.fetchall()
         setPoint2 = results[0][0]

      except:
         try:
            cur = conn.cursor()
            sql = ("SELECT setPoint FROM SetpointLookup WHERE windChill = %s", (windChill))
            cur.execute(*sql)
            results = cur.fetchall()
            setPoint2 = results[0][0]

         except:
            print "setpoint error"
            logging.debug(timeStamp)
            logging.debug('setpoint error')
            
   if(windChillAvg < 71):
      setpointOffset = 0
   else:
      try:
         cur = conn.cursor()
         sql = ("SELECT setPointOffset FROM SetpointLookup WHERE avgWindChill = %s", (windChillAvg))
         cur.execute(*sql)
         results = cur.fetchall()
         setpointOffset = results[0][0]
      except:
         try:
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
   setPoint2 = setPoint2 - setpointOffset
   if (mode == 0):
       valveFlag = 0
   else:
        valveFlag = 1
   cur_eff_sp = setPoint2 + parameterX
   #Constrain effective setpoint
   try:
       spMinFile = open("/usr/local/bin/spMin.txt","r")
       buf = spMinFile.readline()
       spMin = float(buf)
   except:
       print "Unable to open file to read"
       logging.debug(timeStamp)
       logging.debug('Unable to open spMin.txt to read')
   try:
       spMaxFile = open("/usr/local/bin/spMax.txt","r")
       buf = spMaxFile.readline()
       spMax = float(buf)
   except:
       print "Unable to open file to read"
       logging.debug(timeStamp)
       logging.debug('Unable to open spMax.txt to read')
              
   if(cur_eff_sp > spMax):
       cur_eff_sp = spMax
   elif(cur_eff_sp < spMin):
       cur_eff_sp = spMin

   if (cur_eff_sp!=prev_eff_sp):
       os.system("sudo python /home/pi/Desktop/Chronos/write_sp.py")
   prev_eff_sp = cur_eff_sp
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

   for chiller in range(0,4):
       nowTime = time.time()
       timeGap = nowTime-startTime
       if MO_C[chiller] == 0:
           if ((mode==1) & ((setPoint2 + parameterX + t1) <= returnTemp)):
              
               if ((nCon==p[chiller]) & (timeGap>=CCT)):
                   b[chiller] = 1                 
                   nCon = nCon + 1
                   nCmax = nCmax + 1
                   startTime = time.time()
           elif ((mode==1) & ((setPoint2 + parameterX - t1) > returnTemp)):
               if nCon == 0:
                   b[chiller] = 0
                   startTime = time.time()
               elif (((nCmax-nCon)==p[chiller]) & (timeGap>CCT)):
                   b[chiller] = 0
                   nCon = nCon - 1
                   startTime = time.time()
           elif (mode==0):
               b[chiller]=0
       elif MO_C[chiller] == 1:
           b[chiller] = 1
       elif MO_C[chiller] == 2:
           b[chiller] = 0
           
   if (valveFlag!=valveStatus):
     if(valveFlag == 0):
       GPIO.output(valve1Pin, True)
       GPIO.output(valve2Pin, False)
     elif(valveFlag == 1):
       GPIO.output(valve2Pin, True)
       GPIO.output(valve1Pin, False)
     valveStatus = valveFlag
     # time.sleep(120)
       
   
   GPIO_change = 0
   boiler_change = 0
   for i in range (0,4):
       chillerChange[i] = 0
   if boilerStatus != a:
       boilerStatus = a
       boiler_change = 1
       GPIO_change = 1
   for chiller in range (0,4):
       if chillerStatus[chiller] != b[chiller]:
           chillerStatus[chiller] = b[chiller]
           GPIO.output(chillerPin[chiller],chillerStatus[chiller])
           cTime[chiller] = (time.strftime("%Y-%m-%d "), time.strftime("%H:%M:%S"))
           startTime=time.time()
           if (chillerStatus[chiller]==0): 
              sortTime[chiller] = time.time()
           cStatus[chiller]=chillerStatus[chiller]
           chillerChange[chiller] = 1
           GPIO_change = 1
           if (nCon==0):
              curTime = time.time()
              nCmax = 0
              for chiller in range(0,4):
                  sortGap[chiller] = curTime - sortTime[chiller]
                  p[chiller]=0
              for i in range(0,4):
                for j in range (0,(4-i)):
                  if(sortGap[i]<sortGap[i+j]):
                                               p[i] = p[i]+1
                  else:
                       p[i+j] = p[i+j]+1
              for i in range(0,4):
                  p[i] = p[i]-1         

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


   # Update Databases
   try:
      cur = conn.cursor()
      cmd_main = ("UPDATE mainTable SET outsideTemp=%s, waterOutTemp=%s, returnTemp=%s, boilerStatus=%s, chiller1Status=%s, chiller2Status=%s, chiller3Status=%s, chiller4Status=%s, setPoint2=%s, windSpeed=%s ORDER BY LID DESC LIMIT 1", (outsideTemp, waterOutTemp, returnTemp, boilerStatus, chillerStatus[0], chillerStatus[1], chillerStatus[2], chillerStatus[3], setPoint2, windSpeed))
      cur.execute(*cmd_main)
      conn.commit()
   except:
      print 'Error updating mainTable'
      logging.debug(timeStamp)
      logging.debug('Error updating mainTable')
      conn.rollback()

   try:
      cur = conn.cursor()
      cmd_main = ("UPDATE errTable SET err_T1=%s, err_T2=%s, err_Web=%s, err_GPIO=%s, err_DB=%s", (error_T1, error_T2, error_Web, error_GPIO, error_DB))
      cur.execute(*cmd_main)
      conn.commit()
   except:
      print 'Error updating errTable'
      logging.debug(timeStamp)
      logging.debug('Error updating errTable')
      conn.rollback()
   errData = [error_T1, error_T2, error_DB, error_Web, error_GPIO]
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
          cur = conn.cursor()
          if boiler_change == 1:
             cmd_b = ("UPDATE actStream SET timeStamp=%s, status=%s WHERE TID=1", (bTime, bStatus))
             cur.execute(*cmd_b)
          if chillerChange[0] == 1:
             cmd_c1 = ("UPDATE actStream SET timeStamp=%s, status=%s WHERE TID=2", ((cTime[0][0]+cTime[0][1]), cStatus[0]))
             cur.execute(*cmd_c1)
          if chillerChange[1] == 1:
             cmd_c2 = ("UPDATE actStream SET timeStamp=%s, status=%s WHERE TID=3", ((cTime[1][0]+cTime[1][1]), cStatus[1]))
             cur.execute(*cmd_c2)
          if chillerChange[2] == 1:
             cmd_c3 = ("UPDATE actStream SET timeStamp=%s, status=%s WHERE TID=4", ((cTime[2][0]+cTime[2][1]), cStatus[2]))
             cur.execute(*cmd_c3)
          if chillerChange[3] == 1:
             cmd_c4 = ("UPDATE actStream SET timeStamp=%s, status=%s WHERE TID=5", ((cTime[3][0]+cTime[3][1]), cStatus[3]))
             cur.execute(*cmd_c4)
          conn.commit()
       except:
          print 'Error updating actStream'
          logging.debug(timeStamp)
          logging.debug('Error updating actStream')
          conn.rollback()
  
conn.close()
GPIO.cleanup()

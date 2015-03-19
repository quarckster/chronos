#!/usr/bin/python

import urllib2
import os
import commands
import sre
import MySQLdb
import time
from time import strftime
datetime = (time.strftime("%Y-%m-%d ") + time.strftime("%H:%M:00"))
import logging
LOG_FILENAME = '/home/pi/Desktop/Chronos/log_Chronos_sec.out'
logging.basicConfig(filename=LOG_FILENAME,
                    level=logging.INFO
                    )

try:
    readfile = open('/var/www/systemUp.txt', 'r')
    inputstr = (readfile.readlines())
    count = int (inputstr[1])
except:
       print "FileReadError"
       logging.debug(datetime)
       logging.debug('FileReadError')
       count = 0

# -----Insert into DB-----
conn = MySQLdb.connect(host="localhost",user="root",passwd="estrrado",db="Chronos")
cur = conn.cursor()
sql = "SELECT * FROM mainTable ORDER BY logdatetime DESC LIMIT 1"

try:
    cur.execute(sql)
    results = cur.fetchall()
    for row in results:
        outsideTemp = row[2]
        waterOutTemp = row[3]
        returnTemp = row[4]
        boilerStatus = row[5]
        chiller1Status = row[6]
        chiller2Status = row[7]
        chiller3Status = row[8]
        chiller4Status = row[9]
        setPoint2 = row[10]
        parameterX = row[11]
        t1 = row[12]
        MO_B = row[13]
        MO_C1 = row[14]
        MO_C2 = row[15]
        MO_C3 = row[16]
        MO_C4 = row[17]
        mode = row[18]
        powerMode = row[19]
        CCT = row[20]
        windSpeed = row[21]

    sql = "INSERT INTO mainTable (logdatetime,outsideTemp,waterOutTemp,returnTemp,boilerStatus,chiller1Status,chiller2Status,chiller3Status,chiller4Status,setPoint2,parameterX,t1,MO_B,MO_C1,MO_C2,MO_C3,MO_C4,mode,powerMode,CCT,windSpeed) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (datetime,outsideTemp,waterOutTemp,returnTemp,boilerStatus,chiller1Status,chiller2Status,chiller3Status,chiller4Status,setPoint2,parameterX,t1,MO_B,MO_C1,MO_C2,MO_C3,MO_C4,mode,powerMode,CCT,windSpeed)
    cur.execute(*sql)
    conn.commit()
    conn.close()
except:
    print 'Error inserting row'
    logging.debug(datetime)
    logging.debug('Error inserting row')
    conn.rollback()
    conn.close()
# -----insert into DB-----
try:
   output = commands.getoutput("ps aux | grep /home/pi/Desktop/Chronos/Chronos_main.py")
   if 'python' in output:
       error_system = "ONLINE"
       count = 0
   else:
       error_system = "OFFLINE"
       count=count+1
   dataFile = open('/var/www/systemUp.txt', 'w')
   dataFile.write(error_system)
   dataFile.write('\n' + str(count))
   
except:
   print "SystemCheckError"
   logging.debug(datetime)
   logging.debug('SystemCheckError')

try:
    if (count > 2) :
       os.system("sudo python /home/pi/Desktop/Chronos/Chronos_starter.py")
       dataFile = open('/var/www/systemDown.txt', 'a')
       dataFile.write('\n' + str(datetime))
except:
   print "FileWriteError"
   logging.debug(datetime)
   logging.debug('FileWriteError')
       
try:
   output = commands.getoutput("ps aux | grep /home/pi/Desktop/Chronos/led_trial2.py")
   if 'python' in output:
       error=0
   else:
       error=1
       os.system("sudo python /home/pi/Desktop/Chronos/led_starter.py")
   
except:
   print "SystemCheckError"
   logging.debug(datetime)
   logging.debug('SystemCheckError')
   

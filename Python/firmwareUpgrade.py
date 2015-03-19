#!/usr/bin/python

import os
import MySQLdb
import time

powerMode = 0

os.system("sudo kill $(ps aux | grep Chronos_main.py | awk '{print $2 }')")

while((powerMode!=3) & (powerMode!=4)):
    time.sleep(1)
    conn = MySQLdb.connect(host="localhost",user="root",passwd="estrrado",db="Chronos")
    cur = conn.cursor()
    sql = "SELECT * FROM mainTable ORDER BY LID DESC LIMIT 1"
    cur.execute(sql)
    results = cur.fetchall()
    for row in results:
        powerMode = row[17]          
    conn.close()

if (powerMode == 3):
    print "Successful upgrade! Please wait while the new code is initialised."
elif (powerMode == 4):
    print "File transfer failed! Please wait while the main code is restarted."

os.system("sudo python /home/pi/Desktop/Chronos/Chronos_starter.py")

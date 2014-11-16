#!/usr/bin/python

import MySQLdb

count = 0
windChill = 0
conn = MySQLdb.connect(host="localhost",user="root",passwd="estrrado",db="Chronos")
cur = conn.cursor()
cur.execute("""SELECT mode FROM mainTable ORDER BY LID DESC LIMIT 1""")
a = cur.fetchall()
mode = a[0][0]
cur.execute("""SELECT outsideTemp FROM mainTable WHERE logdatetime > DATE_SUB(CURDATE(), INTERVAL 24 HOUR) AND mode = %s ORDER BY LID DESC LIMIT 1440""",(mode))
results = cur.fetchall()
for value in results:
    windChill = windChill + value[0]
    count = count + 1
if (count != 0):    
    windChillAvg = round(windChill/count)
#    print windChill
#    print windChillAvg
    dataFile = open('/home/pi/Desktop/Chronos/windChillAvg.txt', 'w')
    dataFile.write(str(windChillAvg))
    dataFile.close()

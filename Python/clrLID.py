#!/usr/bin/python

import MySQLdb

conn = MySQLdb.connect(host="localhost",user="root",passwd="estrrado",db="Chronos")
cur = conn.cursor()

cur.execute("""SELECT LID FROM `mainTable` WHERE logdatetime >= DATE_SUB(CURDATE(), INTERVAL 4 DAY) ORDER BY LID ASC LIMIT 1""")
a = cur.fetchall()
clrLID = a[0][0]
dataFile = open('/home/pi/Desktop/Chronos/clrLID.txt', 'w')
dataFile.write(str(clrLID))
dataFile.close()

#os.system("sudo pkill python")

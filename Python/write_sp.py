#!/usr/bin/python
try:
   conn = MySQLdb.connect(host="localhost",user="root",passwd="estrrado",db="Chronos")
   cur = conn.cursor()
   sql = "SELECT setPoint2 FROM mainTable ORDER BY LID DESC LIMIT 1"
   cur.execute(sql)
   results = cur.fetchall()
   setPoint2 = results[0][0]           
   conn.close()
except:
    print "Error getting setpoint"
try:
   conn = MySQLdb.connect(host="localhost",user="root",passwd="estrrado",db="Chronos")
   cur = conn.cursor()
   sql = "SELECT parameterX FROM mainTable ORDER BY LID DESC LIMIT 1"
   cur.execute(sql)
   results = cur.fetchall()
   parameterX = results[0][0]           
   conn.close()
except:
    print "Error getting setpoint"

effSetpoint = setPoint2 + parameterX

try:
   dataFile = open('/usr/local/bin/sp.txt', 'w')
   dataFile.write(effSetpoint)
   dataFile.close()
except:
    print "Error opening sp.txt"

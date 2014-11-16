#!/usr/bin/python
import smtplib
import MySQLdb
import os
import time
flag1 = 0
flag2 = 0
prevInTemp = 0
prevOutTemp = 0
print flag1, flag2
conn = MySQLdb.connect(host="localhost",user="root",passwd="estrrado",db="Chronos")
cur = conn.cursor()
sql = "SELECT returnTemp, waterOutTemp FROM mainTable WHERE logdatetime > DATE_SUB(CURDATE(), INTERVAL 8 MINUTE) ORDER BY LID DESC LIMIT 8"
cur.execute(sql)
results = cur.fetchall()
for value in results:
    print value
    
    if (value[0] == prevInTemp):
       flag1 = flag1 + 1
    if (value[1] == prevOutTemp):
       flag2 = flag2 + 1
    prevInTemp = value[0]
    prevOutTemp = value[1]
    
print flag1, flag2

if((flag1 >= 7) & (flag2 >= 7)):
     try:
         os.system("""echo "Please note : A possible lock in the Chronos system has been detected." | mail -s "Chronos Issue Notifier" benjamin@estrrado.com""")
         os.system("""echo "Please note : A possible lock in the Chronos system has been detected." | mail -s "Chronos Issue Notifier" thebenonlyn@gmail.com""")
         os.system("""echo "Please note : A possible lock in the Chronos system has been detected." | mail -s "Chronos Issue Notifier" sanjumathew.ieee@gmail.com""")
         os.system("""echo "Please note : A possible lock in the Chronos system has been detected." | mail -s "Chronos Issue Notifier" adam.thomas@gmail.com""")
         os.system("""sudo python /home/pi/Desktop/Chronos/sendEmail2.py""")
         time.sleep(5)
         os.system("""sudo pkill python""")
         os.system("""sudo python /home/pi/Desktop/Chronos/Chronos_starter.py""")
     except:
         print ""
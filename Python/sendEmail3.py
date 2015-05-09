#!/usr/bin/python

import smtplib
import MySQLdb
sender = 'arun@estrrado.com'
receivers = ['benjamin@estrrado.com']
message1 = """From: Arun <arun@estrrado.com>
To: Benjamin <benjamin@estrrado.com>
Subject: Chronos Status Notifier
     
CHRONOS v2.0
Serial No: CHRON003
Current system status :
     """
try:
       conn = MySQLdb.connect(host="localhost",user="root",passwd="estrrado",db="Chronos")
       cur = conn.cursor()
       sql = "SELECT * FROM mainTable ORDER BY LID DESC LIMIT 1"
       cur.execute(sql)
       results = cur.fetchall()
       for row in results:
           logdatetime = row[1]
           outsideTemp = row[2]
           waterOutTemp = row[3]
           returnTemp = row[4]
           setPoint2 = row[10]
           parameterX = row[11]
           t1 = row[12]
           MO_B = row[13]
           MO_C1 = row[14]
           MO_C2 = row[15]
           MO_C3 = row[16]
           MO_C4 = row[17]
           mode = row[18]
           windSpeed = row[21]
       sql = "SELECT * FROM errTable"
       cur.execute(sql)
       results = cur.fetchall()
       for row in results:
           err_T1 = row[0]
           err_T2 = row[1]
           err_Web = row[2]
           err_GPIO = row[3]
           err_DB = row[4]
       sql = "SELECT * FROM actStream WHERE TID=1"
       cur.execute(sql)
       results = cur.fetchall()
       for row in results:
           boilerTime = row[1]
           boilerStatus = row[2]
       sql = "SELECT * FROM actStream WHERE TID=2"
       cur.execute(sql)
       results = cur.fetchall()
       for row in results:
           chiller1Time = row[1]
           chiller1Status = row[2]
       sql = "SELECT * FROM actStream WHERE TID=3"
       cur.execute(sql)
       results = cur.fetchall()
       for row in results:
           chiller2Time = row[1]
           chiller2Status = row[2]
       sql = "SELECT * FROM actStream WHERE TID=4"
       cur.execute(sql)
       results = cur.fetchall()
       for row in results:
           chiller3Time = row[1]
           chiller3Status = row[2]
       sql = "SELECT * FROM actStream WHERE TID=5"
       cur.execute(sql)
       results = cur.fetchall()
       for row in results:
           chiller4Time = row[1]
           chiller4Status = row[2]
       
       conn.close()       
except:
       print "Error fetching data from DB"

if (mode == 0):
   mode = ("""Winter mode.""")
else:
     mode = ("""Summer mode""")
if (boilerStatus == 1):
   boilerStatus = ("""ON""")
else:
     boilerStatus = ("""OFF""")
if (chiller1Status == 1):
   chiller1Status = ("""ON""")
else:
     chiller1Status = ("""OFF""")
if (chiller2Status == 1):
   chiller2Status = ("""ON""")
else:
     chiller2Status = ("""OFF""")
if (chiller3Status == 1):
   chiller3Status = ("""ON""")
else:
     chiller3Status = ("""OFF""")
if (chiller4Status == 1):
   chiller4Status = ("""ON""")
else:
     chiller4Status = ("""OFF""")
if (MO_B == 0):
   MO_B = ("""Auto""")
elif (MO_B == 1):
   MO_B = ("""ON""")
else:
     MO_B = ("""OFF""")
if (MO_C1 == 0):
   MO_C1 = ("""Auto""")
elif (MO_C1 == 1):
   MO_C1 = ("""ON""")
else:
     MO_C1 = ("""OFF""")
if (MO_C2 == 0):
   MO_C2 = ("""Auto""")
elif (MO_C2 == 1):
   MO_C2 = ("""ON""")
else:
     MO_C2 = ("""OFF""")
if (MO_C3 == 0):
   MO_C3 = ("""Auto""")
elif (MO_C3 == 1):
   MO_C3 = ("""ON""")
else:
     MO_C3 = ("""OFF""")
if (MO_C4 == 0):
   MO_C4 = ("""Auto""")
elif (MO_C4 == 1):
   MO_C4 = ("""ON""")
else:
     MO_C4 = ("""OFF""")
sysUpFile = open("/var/www/systemUp.txt","r")
sysUp = sysUpFile.readline()

message2 = ("""System """ + str(sysUp) + """   Mode : """ + str(mode))
if (err_T1 == 0):
   message2_1 = ("""\nTemp sensor 1 - ONLINE""")
else:
     message2_1 = ("""\nTemp sensor 1 - OFFLINE""")
if (err_T2 == 0):
   message2_2 = ("""\nTemp sensor 2 - ONLINE""")
else:
     message2_2 = ("""\nTemp sensor 2 - OFFLINE""")
if (err_Web == 0):
   message2_3 = ("""\nInternet Connectivity - ONLINE""")
else:
     message2_3 = ("""\nInternet Connectivity - OFFLINE""")
if (err_DB == 0):
   message2_4 = ("""\nDatabase connectivity - ONLINE""")
else:
     message2_4 = ("""\nDatabase connectivity - OFFLINE""")
if (err_GPIO == 0):
   message2_5 = ("""\nGPIO module - ONLINE""")
else:
     message2_5 = ("""\nGPIO module - OFFLINE""")
message3 = ("""\nDB Last updated at """ + str(logdatetime) + """\n""")
message4 = ("""\nOutside Temperature : """ + str(outsideTemp))
message5 = ("""\nOutlet Temperature : """ + str(waterOutTemp))
message6 = ("""\nInlet Temperature : """ + str(returnTemp))
message7 = ("""\nBoiler """ + str(boilerStatus) + """ since """ + str(boilerTime))
message8 = ("""\nChiller 1 """ + str(chiller1Status) + """ since """ + str(chiller1Time))
message9 = ("""\nChiller 2 """ + str(chiller2Status) + """ since """ + str(chiller2Time))
message9_1 = ("""\nChiller 3 """ + str(chiller3Status) + """ since """ + str(chiller3Time))
message9_2 = ("""\nChiller 4 """ + str(chiller4Status) + """ since """ + str(chiller4Time))
message10 = ("""\nCurrent Setpoint : """ + str(setPoint2))
message11 = ("""\nSystem Parameters : """ + str(parameterX) + """, """ + str(t1))
message12 = ("""\nBoiler Override : """ + str(MO_B))
message13 = ("""\nChiller1 Override : """ + str(MO_C1))
message14 = ("""\nChiller2 Override : """ + str(MO_C2))
message14_1 = ("""\nChiller3 Override : """ + str(MO_C3))
message14_2 = ("""\nChiller4 Override : """ + str(MO_C4))
message15 = """\n\nYou have received this email as a result of your subsciption to the Chronos status notifier mailing list. If you wish to unsubscribe, please contact your local Chronos system administrator."""
message = message1 + message2 + message3 + message2_1 + message2_2 + message2_3 + message2_4 + message2_5 + """\n""" + message7 + message8 + message9 + message9_1 + message9_2 + """\n""" + message4 + message6 + message5 + message10 + """\n""" + message12 + message13 + message14 + message11 + """\n""" + message15
#print message
#smtpObj = smtplib.SMTP('mail.estrrado.com', 26)
#smtpObj.sendmail(sender, receivers, message)

try:
     smtpObj = smtplib.SMTP('mail.estrrado.com', 26)
     smtpObj.sendmail(sender, receivers, message)
except:
     print "Error: unable to send email"

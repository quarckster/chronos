#!/usr/bin/python
import MySQLdb
import time
import os

os.system("sudo crontab -l > $HOME/scrontab_file")
os.system("sudo crontab -r")
try:
   os.system("sudo kill $(ps aux | grep Chronos_main.py | awk '{print $2 }')")
except:
   try:
       os.system("sudo kill $(ps aux | grep Chronos_main.py | awk '{print $2 }')")
   except:
       print "kill error"
      
os.system("sudo python /home/pi/Desktop/Chronos/clrLID.py")
try:
    clrFile = open("/home/pi/Desktop/Chronos/clrLID.txt","r")
    clrLID = int(clrFile.read(4))
except:
    print "Unable to read file."
    clrLID = 1440
    
try:
    conn = MySQLdb.connect(host="localhost",user="root",passwd="estrrado",db="Chronos")
    cur = conn.cursor()
    cur.execute("""DELETE FROM mainTable WHERE LID < %s""", clrLID)
    conn.commit()
    cur.execute("""SELECT LID FROM mainTable ORDER BY LID DESC LIMIT 1""")
    b1 = cur.fetchall()
    cur.execute("""SELECT LID FROM mainTable ORDER BY LID ASC LIMIT 1""")
    a1 = cur.fetchall()
    #print a1[0][0],b1[0][0]
    a = a1[0][0]
    b = b1[0][0]
    c = b - a
    #print c
    for d in range (c+1):
        a2=a+d
        cur.execute("""UPDATE `mainTable` SET LID=%s  WHERE LID=%s""",((d+1), a2))
        conn.commit()

    cur.execute("""SELECT LID FROM mainTable ORDER BY LID DESC LIMIT 1""")
    b1 = cur.fetchall()
    b = b1[0][0]
    cur.execute("""ALTER TABLE mainTable AUTO_INCREMENT=%s""",(b))
    conn.commit()
    conn.close()
except:
    print 'Error while deleting DB values'
    conn.rollback()
    
os.system("sudo crontab $HOME/scrontab_file")
os.system("sudo python /home/pi/Desktop/Chronos/Chronos_starter.py")

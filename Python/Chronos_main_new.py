#!/usr/bin/env python

import time
import datetime
import logging
import os
import MySQLdb
import urllib2
import sre
import subprocess
import signal
import errno
import lxml
import RPi.GPIO as GPIO

LOG_FILENAME = "home/pi/Desktop/Chronos/log_Chronos.out"
logging.basicConfig(filename=LOG_FILENAME,
                    level=logging.DEBUG,
                    datefmt="%Y-%m-%d %H:%M:%S"
                    format="%(asctime)s %(levelname)s:%(message)s")
timeStamp = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:00")
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
a = 0
b = 0
c = 0
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
except Exception as e:
    error_GPIO = 1
    GPIO.output(led_red,True)
    time.sleep(0.7)
    GPIO.output(led_red,False)
    logging.exception("ErrorGPIO: %s" % e)

#-----temp sensors-----
sensorOutID = "28-00042d4367ff"
sensorInID = "28-00042c648eff"
#sensorOutID = '28-00000677d162'
#sensorInID = '28-00000676e315'
# os.system('modprobe w1-gpio')
# os.system('modprobe w1-therm')

#-----kill related programs-----
# try:
#    os.system("sudo kill $(ps aux | grep firmwareUpgrade.py | awk '{print $2 }')")
# except:
#    print "killError"
#    GPIO.output(led_red,True)
#    time.sleep(0.7)
#    GPIO.output(led_red,False)
#    logging.debug(timeStamp)
#    logging.debug('killError')

# try:
#    os.system("sudo kill $(ps aux | grep Chronos_starter.py | awk '{print $2 }')")
# except:
#    print "killError2"
#    GPIO.output(led_red,True)
#    time.sleep(0.7)
#    GPIO.output(led_red,False)
#    logging.debug(timeStamp)
#    logging.debug('killError2')

try:
    conn = MySQLdb.connect(host="localhost",
                           user="raspberry",
                           passwd="estrrado",
                           db="Chronos")
except MySQLdb.Error as e:
    time.sleep(5)
    logging.exception("Cannot connect to DB: %s" % e)
    GPIO.cleanup()
    sys.exit(1)

#-----reset DB values-----
def reset_db_values():
    try:
        with conn:
            cur = conn.cursor()
            sql1 = """UPDATE mainTable SET boilerStatus=%s, chiller1Status=%s,
                   chiller2Status=%s, chiller3Status=%s, chiller4Status=%s,
                   MO_B=%s, MO_C1=%s, MO_C2=%s, MO_C3=%s, MO_C4=%s,
                   powerMode=%s ORDER BY LID DESC LIMIT 1
                   """ % (boilerStatus, chillerStatus[0], chillerStatus[1],
                          chillerStatus[2], chillerStatus[3], MO_B, MO_C[0],
                          MO_C[1], MO_C[2], MO_C[3], powerMode)
            sql2 = ("UPDATE actStream SET timeStamp=%s, status=%s" %
                   (timeStamp, boilerStatus))
            cur.execute(sql1)
            cur.execute(sql2)
    except MySQLdb.Error as e:
        logging.exception("Error while resetting DB values: %s" % e)
        GPIO.output(led_red,True)
        time.sleep(0.7)
        GPIO.output(led_red,False)

# -----|| The main stuff ||-----
print "Starting script..."

# while True:
time.sleep(2)
timeStamp = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")

def manage_system():
    "Check for shutdown, restart, etc."
    if powerMode == 10:
        subprocess.call(["reboot"])
    elif powerMode == 20:
        subprocess.call(["shutdown", "now"])
    elif powerMode == 2:
        subprocess.call(["python", FIRMWARE_UPGRADE])
     # os.system("sudo python /home/pi/Desktop/Chronos/firmwareUpgrade.py")
        time.sleep(10)
    elif powerMode == 7:
        subprocess.call(["python", "/home/pi/Desktop/Chronos/Chronos_starter.py"])
        time.sleep(10)

def is_process_exists(process_name):
    pids = [x for x in reversed(os.listdir("/proc")) if x.isdigit()]
    for pid in pids:
        with open(os.path.join("/proc", pid, "cmdline")) as cmdline:
            ps = cmdline.read().strip()
        if process_name in ps:
            result = True
            break
        elif pid == pids[-1] and process_name not in ps:
            result = False
    return result

def check_mysql():
    "Check if MySQL service is running."
    if is_process_exist("mysqld"):
        error_DB = 0
    else:
        error_DB = 1
        GPIO.output(led_red,True)
        time.sleep(0.7)
        GPIO.output(led_red,False)
    return error_DB

def read_temp(device_file):
    while True:
        with open(device_file) as content:
            lines = content.readlines()
        if lines[0].strip()[-3:] == "YES":
            break
        else:
            time.sleep(0.2)
    equals_pos = lines[1].find("t=")
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp = float(temp_string) / 1000.0 # Divide by 1000 for proper decimal point
        temp = temp * 9.0 / 5.0 + 32.0 # Convert to degF
        temp = round(temp, 1) # Round temp to 2 decimal points
        return temp

def read_temperature_sensors():
    "Read Temperature Sensors."
    error_T1 = 1
    error_T2 = 1
    base_dir = "/home/pi/fake_sys/"
    for directory in os.listdir(base_dir):
        if directory in (sensorInID, sensorOutID):
            device_folder = os.path.join(base_dir, directory)
            # glob.glob(base_dir + '28*')[sensors]
            print device_folder
            device_file = os.path.join(device_folder, "w1_slave")
            device_file_ID = os.path.join(device_folder, "name")
            device_id = ""
            try:
                with open(device_file_ID) as content:
                    device_id = content.read(15)
            except IOError as e:
                if e.errno == errno.ENOENT:
                    pass
            try:
                with open(device_file) as content:
                    temp_raw = content.readlines()
            except IOError as e:
                if e.errno == errno.ENOENT:
                    print "Temp sensor error:", str(e)
                    logging.exception("Temp sensor error: %s" % e)
                    GPIO.output(led_red, True)
                    time.sleep(0.7)
                    GPIO.output(led_red, False)
                    with conn:
                        cur = conn.cursor()
                        sql = "SELECT returnTemp FROM mainTable ORDER BY LID DESC LIMIT 1"
                        cur.execute(sql)
                        results = cur.fetchone()
                    returnTemp = results[0]
            if device_id == sensorOutID:
                waterOutTemp = read_temp(device_file)
                print "SensorOutID is %s. Temp is %s" % (device_id, waterOutTemp)
                error_T2 = 0
            elif device_id == sensorInID:
                returnTemp = read_temp(device_file)
                print "SensorInID is %s. Temp is %s" % (device_id, returnTemp)
                error_T1 = 0
    return waterOutTemp, returnTemp

def blink_leds(waterOutTemp, breather_count):
    if waterOutTemp > temp_thresh:
        led_breather = led_red
    else:
        led_breather = led_blue 
    if breather_count == 0:     
        GPIO.output(led_breather, True)
        time.sleep(0.1)
        GPIO.output(led_breather, False)
        time.sleep(0.1)
        GPIO.output(led_breather, True)
        time.sleep(0.1)
        GPIO.output(led_breather, False)
        time.sleep(0.1)
        breather_count += 1
    else:
        breather_count = 0
    return breather_count

def read_values_from_db(waterOutTemp):
    "Read values from DB."
    try:
        with conn:
            cur = conn.cursor()
            sql = "SELECT * FROM mainTable ORDER BY LID DESC LIMIT 1"
            cur.execute(sql)
            result = cur.fetchone()
            boilerStatus = result[5]
            chillerStatus[0] = result[6]
            chillerStatus[1] = result[7]
            chillerStatus[2] = result[8]
            chillerStatus[3] = result[9]
            setPoint2 = result[10]
            parameterX = result[11]
            t1 = result[12]
            MO_B = result[13]
            MO_C[0] = result[14]
            MO_C[1] = result[15]
            MO_C[2] = result[16]
            MO_C[3] = result[17]
            mode = result[18]
            powerMode = result[19]
            CCT = result[20]
    except MySQLdb.Error as e:
        print "Error fetching data from DB"
        logging.exception("Error fetching data from DB: %s" % e)
        GPIO.output(led_red,True) 
        time.sleep(0.7)
        GPIO.output(led_red,False)
    return {"boilerStatus": boilerStatus,
            "chillerStatus1": chillerStatus[0],
            "chillerStatus2": chillerStatus[1],
            "chillerStatus3": chillerStatus[2],
            "chillerStatus4": chillerStatus[3],
            "setPoint2": setPoint2,
            "parameterX": parameterX,
            "t1": t1, "MO_B": MO_B,
            "MO_C1": MO_C[0], "MO_C2": MO_C[1],
            "MO_C3": MO_C[2], "MO_C4": MO_C[3],
            "mode": mode, "powerMode": powerMode,
            "CCT": CCT*60}


   # CCT = CCT*60
def get_wind_speed_from_url():
    """Get wind speed from wx.thomaslivestock.com.

    Use lxml for parsing html.
    Returns:
       INT: wind speed
    """
    try:
        content = urllib.urlopen(url)
    except IOError as e:
        turn_off_fountain()
        destructor()
        sys.exit("Can't retrieve the url: %s" % e)
    html = content.read()
    tree = etree.HTML(html)
    node = tree.xpath(
        "/html/body/table/tr/td/font/strong/font/small/text()")[1]
    wind_speed = float(node.split()[2])
    print("The current windspeed from wx.thomaslivestock.com "
         "is %d MPH" % wind_speed)
    return wind_speed

def get_data_from_web(mode):
    "Parsing windChill and windSpeed from wx.thomaslivestock.com."
    error_Web = 0
    try:
        content = urllib2.urlopen('http://wx.thomaslivestock.com')
    except IOError:
        print 'Unable to get data from website'
        print 'Reading previous value from DB'
        logging.exception("Unable to get data from website. Reading previous value from DB.")
        error_Web = 1
        GPIO.output(led_red, True)
        time.sleep(0.7)
        GPIO.output(led_red, False)
        try:
            with conn:
                cur = conn.cursor()
                sql = "SELECT outsideTemp, windSpeed FROM mainTable ORDER BY LID DESC LIMIT 1"
                cur.execute(sql)
                results = cur.fetchone()
                outsideTemp = results[0]
                windSpeed = results[1]
            except MySQLdb.Error:
                print 'Unable to get value from DB'
                print 'Reverting to default value of 65 deg F...'
                logging.exception("Unable to get value from DB. Reverting to default value of 65 deg F...")
                outsideTemp = 65.00
                windSpeed = 0.00
    else:
        html = content.read()
        tree = etree.HTML(html)
        # Wind Chill
        if mode == 0:
            node = tree.xpath(
                "/html/body/table/tr[10]/td[2]/font/strong/font/small/text()")
        # Temperature
        elif mode == 1:
            node = tree.xpath(
                "/html/body/table/tr[3]/td[2]/font/strong/small/font/text()")
        outTemp = node[0].split(u"\xb0F")[0]
        outsideTemp = float(outTemp)
        node = tree.xpath(
            "/html/body/table/tr[6]/td[2]/font/strong/font/small/text()")
        wind_speed = float(node[0].split()[2])
    return {"outsideTemp": outsideTemp,
            "windSpeed": wind_speed,
            "error_Web": error_Web}

def calculate_setpoint(outsideTemp, setPoint2, parameterX):
    "Calculate setpoint from windChill."
    windChill = int(outsideTemp)
    try:
        with open("/home/pi/Desktop/Chronos/windChillAvg.txt") as windChillFile:
            buf = windChillFile.read(3)
            index = buf.find(".")
            windChillAvg = int(buf[0:index])
    except IOError as e:
        print "Unable to open file to read"
        logging.exception("Unable to open file to read: %s" % e)
    if windChill < 11:
        setPoint2 = 100
    else:
        try:
            with conn:
                cur = conn.cursor()
                sql = "SELECT setPoint FROM SetpointLookup WHERE windChill = %s" % windChill
                cur.execute(sql)
                results = cur.fetchone()
                setPoint2 = results[0]
        except MySQLdb.Error as e:
            print "setpoint error"
            logging.exception("Setpoint error: %s" % e)
    if windChillAvg < 71:
        setpointOffset = 0
    else:
        try:
            with conn:
                cur = conn.cursor()
                sql = "SELECT setPointOffset FROM SetpointLookup WHERE avgWindChill = %s" % windChillAvg
                cur.execute(sql)
                results = cur.fetchone()
                setpointOffset = results[0]
        except MySQLdb.Error as e:
            setpointOffset = 0
            print "Set point error"
            logging.exception("Set point error: %s" % e)
    setPoint2 -= setpointOffset
    if mode == 0:
        valveFlag = 0
    elif mode == 1:
        valveFlag = 1
    cur_eff_sp = setPoint2 + parameterX
    return {"cur_eff_sp": cur_eff_sp, "valveFlag": valveFlag}

def constrain_effective_setpoint(cur_eff_sp):
    try:
        with open("/usr/local/bin/spMin.txt") as spMinFile:
            buf = spMinFile.readline()
            spMin = float(buf)
    except IOError as e:
        print "Unable to open file to read"
        logging.exception("Unable to open spMin.txt to read: %s" % e)
    try:
        with open("/usr/local/bin/spMax.txt") as spMaxFile:
            buf = spMaxFile.readline()
            spMax = float(buf)
    except IOError as e:
        print "Unable to open file to read"
        logging.exception("Unable to open spMax.txt to read: %s" % e)
    if cur_eff_sp > spMax:
        cur_eff_sp = spMax
    elif cur_eff_sp < spMin:
        cur_eff_sp = spMin
    if cur_eff_sp != prev_eff_sp:
        try:
            with open("/usr/local/bin/sp.txt", "w") as dataFile:
                dataFile.write(str(cur_eff_sp))
        except Exception as e:
            print "Error opening sp.txt"
            logging.exception("Error opening sp.txt: %s" % e)
    return cur_eff_sp

def conditions_check(MO_B, mode, returnTemp, cur_eff_sp, t1):
   # Conditions Check
    if MO_B == 0 :
        if mode == 0 and (returnTemp <= (cur_eff_sp - t1)):
            a = 1
        elif mode == 0 and (returnTemp > (cur_eff_sp + t1)):
            a = 0
        elif mode == 1:
            a = 0
    elif MO_B == 1:
        a = 1
    elif MO_B == 2:
        a = 0
    return a

def chillers_switching(cur_eff_sp, returnTemp, t1, MO_C, CCT, mode):
    for chiller in range(4):
        nowTime = time.time()
        timeGap = nowTime - startTime
        if MO_C[chiller] == 0:
            # if ((mode==1) & ((setPoint2 + parameterX + t1) <= returnTemp)):
            if mode == 1 and (cur_eff_sp + t1) <= returnTemp: 
                if (nCon == p[chiller]) and (timeGap >= CCT) and (nCon < 4):
                    b[chiller] = 1                 
                    if nCon == nCmax:
                       nCmax = nCmax + 1
                    nCon = nCon + 1
                    startTime = time.time()
            # elif ((mode==1) & ((setPoint2 + parameterX - t1) > returnTemp)):
            elif mode == 1 and (cur_eff_sp - t1) > returnTemp:
                if nCon == 0:
                    b[chiller] = 0
                    startTime = time.time()
                elif (((nCmax-nCon)==p[chiller]) & (timeGap>CCT) & (nCon > 0)):
                   b[chiller] = 0
                   nCon = nCon - 1
                   startTime = time.time()
            elif (mode==0):
                b[chiller]=0
        elif MO_C[chiller] == 1:
            b[chiller] = 1
        elif MO_C[chiller] == 2:
            b[chiller] = 0
     cur_eff_sp = prev_eff_sp        
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

def update_db():
    try:
        with conn:
            cur = conn.cursor()
            sql1 = ("""UPDATE mainTable SET outsideTemp=%s,
                    waterOutTemp=%s, returnTemp=%s, boilerStatus=%s,
                    chiller1Status=%s, chiller2Status=%s,
                    chiller3Status=%s, chiller4Status=%s,
                    setPoint2=%s, windSpeed=%s ORDER BY 
                    LID DESC LIMIT 1""" % (outsideTemp, waterOutTemp,
                                           returnTemp, boilerStatus,
                                           chillerStatus[0],
                                           chillerStatus[1],
                                           chillerStatus[2],
                                           chillerStatus[3],
                                           setPoint2,
                                           windSpeed))
            sql2 = ("""UPDATE errTable SET err_T1=%s, err_T2=%s, err_Web=%s,
                    err_GPIO=%s, err_DB=%s""" % (error_T1, error_T2,
                                                 error_Web, error_GPIO,
                                                 error_DB))
            cur.execute(sql1)
            cur.execute(sql2)
    except MySQLdb.Error as e:
        print 'Error updating mainTable'
        logging.exception("Error updating table: %s" % e)
    if GPIO_change == 1:
        sql_timeStamp, sql_status = "", ""
        if boiler_change == 1:
            sql_timeStamp += "WHEN TID=%s THEN %s\n" % (1, bTime)
            sql_status += "WHEN TID=%s THEN %s\n" % (1, bStatus)
        if chillerChange[0] == 1:
            sql_timeStamp += "WHEN TID=%s THEN %s\n" % (2, (cTime[0][0]+cTime[0][1]))
            sql_status += "WHEN TID=%s THEN %s\n" % (2, cStatus[0]))
        if chillerChange[1] == 1:
            sql_timeStamp += "WHEN TID=%s THEN %s\n" % (3, (cTime[1][0]+cTime[1][1]))
            sql_status += "WHEN TID=%s THEN %s\n" % (3, cStatus[1]))
        if chillerChange[2] == 1:
            sql_timeStamp += "WHEN TID=%s THEN %s\n" % (4, (cTime[2][0]+cTime[2][1]))
            sql_status += "WHEN TID=%s THEN %s\n" % (4, cStatus[2]))
        if chillerChange[3] == 1:
            sql_timeStamp += "WHEN TID=%s THEN %s\n" % (5, (cTime[3][0]+cTime[3][1]))
            sql_status += "WHEN TID=%s THEN %s\n" % (5, cStatus[3]))
        s = []
        if sql_timeStamp:
            sql1 = "timeStamp=CASE\n"
            sql1 += sql_timeStamp
            sql1 += "ELSE timeStamp END"
            s.append(sql1)
        if sql_status:
            sql2 = "status=CASE\n"
            sql2 += sql_status
            sql2 = "ELSE status END"
            s.append(sql2)
        if s:
            s = ",\n".join(s)
            sql = "UPDATE actStream SET\n"
            sql += s
            try:
                with conn:
                    cur = conn.cursor()
                    cur.execute(sql)
            except MySQLdb.Error as e:
                logging.exception("Error updating table: %s" % e)

def update_sysStatus(error_T1, error_T2, error_DB, error_Web, error_GPIO):
    errData = [error_T1, error_T2, error_DB, error_Web, error_GPIO]
    try:
        with open("/var/www/sysStatus.txt", "w") as dataFile:
            for item in errData:
                dataFile.write("%s\n" % str(item))
    except IOError as e:
        print "Error opening file to write"
        logging.exception("Error opening file to write: %s" % e)

def destructor():
    if conn:
        conn.close()
    GPIO.cleanup()

if __name__ == '__main__':
    
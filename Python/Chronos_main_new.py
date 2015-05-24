#!/usr/bin/env python

import time
import datetime
import logging
import os
import MySQLdb
import urllib2
import subprocess
import signal
import errno
import sys
import RPi.GPIO as GPIO
from lxml import etree

LOG_FILENAME = "/var/log/chronos.log"
logging.basicConfig(filename=LOG_FILENAME,
                    level=logging.DEBUG,
                    datefmt="%Y-%m-%d %H:%M:%S",
                    format="%(asctime)s %(levelname)s:%(message)s")
logging.debug('Starting script')

# -----variables-----
waterOutTemp = 00.00    #Temp sensor values. Also, the values that they...
returnTemp = 00.00      #    ...fall back to if sensors are not available
boilerStatus = 0        #ON = 1, OFF = 0
#valveStatus = 0
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
# breather_count = 0
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

try:
    conn = MySQLdb.connect(host="localhost",
                           user="raspberry",
                           passwd="estrrado",
                           db="Chronos")
except MySQLdb.Error as e:
    time.sleep(5)
    logging.exception("Cannot connect to DB: %s" % e)
    destructor()
    sys.exit(1)

timeStamp = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")

def reset_db_values():
    #-----reset DB values-----
    try:
        with conn:
            cur = conn.cursor()
            # sql1 = """UPDATE mainTable SET boilerStatus=%s, chiller1Status=%s,
            #        chiller2Status=%s, chiller3Status=%s, chiller4Status=%s,
            #        MO_B=%s, MO_C1=%s, MO_C2=%s, MO_C3=%s, MO_C4=%s,
            #        powerMode=%s ORDER BY LID DESC LIMIT 1
            #        """ % (boilerStatus, chillerStatus[0], chillerStatus[1],
            #               chillerStatus[2], chillerStatus[3], MO_B, MO_C[0],
            #               MO_C[1], MO_C[2], MO_C[3], powerMode)
            sql1 = ("UPDATE mainTable SET boilerStatus=%s, chiller1Status=%s, chiller2Status=%s, chiller3Status=%s, chiller4Status=%s, MO_B=%s, MO_C1=%s, MO_C2=%s, MO_C3=%s, MO_C4=%s, powerMode=%s ORDER BY LID DESC LIMIT 1" % (boilerStatus, chillerStatus[0], chillerStatus[1], chillerStatus[2], chillerStatus[3], MO_B, MO_C[0], MO_C[1], MO_C[2], MO_C[3], powerMode))
            sql2 = ("UPDATE actStream SET timeStamp=\"%s\", status=%s" % (timeStamp, 0))
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
# time.sleep(2)

def manage_system():
    "Check for shutdown, restart, etc."
    if powerMode == 10:
        subprocess.call(["reboot"])
    elif powerMode == 20:
        subprocess.call(["shutdown", "now"])
    elif powerMode == 2:
        subprocess.call(["python", "/home/pi/Desktop/Chronos/firmwareUpgrade.py"])
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
    if is_process_exists("mysqld"):
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
                # print "SensorOutID is %s. Temp is %s" % (device_id, waterOutTemp)
                error_T2 = 0
            elif device_id == sensorInID:
                returnTemp = read_temp(device_file)
                # print "SensorInID is %s. Temp is %s" % (device_id, returnTemp)
                error_T1 = 0
    return {"waterOutTemp": waterOutTemp, "returnTemp": returnTemp,
            "error_T1": error_T1, "error_T2": error_T2}

def blink_leds(waterOutTemp, breather_count=0):
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

def read_values_from_db():
    "Read values from DB."
    try:
        with conn:
            cur = conn.cursor()
            sql = "SELECT * FROM mainTable ORDER BY LID DESC LIMIT 1"
            cur.execute(sql)
            result = cur.fetchone()
            boilerStatus = result[5]
            chillerStatus = [result[6], result[7], result[8], result[9]]
            setPoint2 = result[10]
            parameterX = result[11]
            t1 = result[12]
            MO_B = result[13]
            MO_C = [result[14], result[15], result[16], result[17]]
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
            "chillerStatus": chillerStatus,
            "setPoint2": setPoint2,
            "parameterX": parameterX,
            "t1": t1, "MO_B": MO_B,
            "MO_C": MO_C, "mode": mode,
            "powerMode": powerMode,
            "CCT": CCT*60}

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
    #constrain effective setpoint
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
        except IOError as e:
            print "Error opening sp.txt"
            logging.exception("Error opening sp.txt: %s" % e)
    return {"cur_eff_sp": cur_eff_sp, "valveFlag": valveFlag}

def boiler_switcher(MO_B, mode, returnTemp, cur_eff_sp, t1, boilerStatus):
    now = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    if MO_B == 0:
        if boilerStatus == 0 and mode == 0 and returnTemp <= (cur_eff_sp - t1):
            boilerStatus = 1
            GPIO.output(boilerPin, True)
            update_actStream_table(now, boilerStatus, 1)
        elif boilerStatus == 1 and mode == 0 and returnTemp > (cur_eff_sp + t1):
            boilerStatus = 0
            GPIO.output(boilerPin, False)
            update_actStream_table(now, boilerStatus, 1)
        elif boilerStatus == 1 and mode == 1:
            boilerStatus = 0
            GPIO.output(boilerPin, False)
            update_actStream_table(now, boilerStatus, 1)
    elif MO_B == 1 and boilerStatus == 0:
        boilerStatus = 1
        GPIO.output(boilerPin, True)
        update_actStream_table(now, boilerStatus, 1)
    elif MO_B == 2 and boilerStatus == 1:
        boilerStatus = 0
        GPIO.output(boilerPin, False)
        update_actStream_table(now, boilerStatus, 1)
    return boilerStatus

def chillers_cascade_switcher(cur_eff_sp, chillerStatus, returnTemp, t1, MO_C, CCT, mode, last_turned_off_index,
                              last_turned_on_index, last_switch_time):
    timeGap = time.time() - last_switch_time
    now = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    # Manual override
    skip_indexes = []
    print chillerStatus
    for i, MO_C_item in enumerate(MO_C):
        if MO_C_item == 1:
            if chillerStatus[i] == 0:
                chillerStatus[i] = 1
                GPIO.output(chillerPin[i], chillerStatus[i])
                update_actStream_table(now, chillerStatus[i], i+2)
            skip_indexes.append(i)
        elif MO_C_item == 2:
            if chillerStatus[i] == 1:
                chillerStatus[i] = 0
                GPIO.output(chillerPin[i], chillerStatus[i])
                update_actStream_table(now, chillerStatus[i], i+2)
            skip_indexes.append(i)
    # Turn on chillers
    print timeGap, CCT
    if (returnTemp >= (cur_eff_sp + t1)
        and timeGap >= CCT
        and mode == 1
        and 0 in chillerStatus
        and last_turned_on_index not in skip_indexes):
        chillerStatus[last_turned_on_index] = 1
        print chillerStatus[last_turned_on_index]
        GPIO.output(chillerPin[last_turned_on_index], chillerStatus[last_turned_on_index])
        update_actStream_table(now, chillerStatus[last_turned_on_index], last_turned_on_index+2)
        last_switch_time = time.time()
        if (last_turned_on_index + 1) == len(chillerStatus):
            last_turned_on_index = 0
        else:
            last_turned_on_index += 1
    # Turn off chillers
    elif ((returnTemp < (cur_eff_sp - t1)
           and timeGap >= CCT
           and 1 in chillerStatus
           and last_turned_off_index not in skip_indexes) or mode == 0):
        chillerStatus[last_turned_off_index] = 0
        GPIO.output(chillerPin[last_turned_off_index], chillerStatus[last_turned_off_index])
        update_actStream_table(now, chillerStatus[last_turned_off_index], last_turned_off_index+2)
        last_switch_time = time.time()
        if (last_turned_off_index + 1) == len(chillerStatus):
            last_turned_off_index = 0
        else:
            last_turned_off_index += 1
    # Turn off chillers when winter
    elif (mode == 0
          and 1 in chillerStatus
          and last_turned_off_index not in skip_indexes):
        chillerStatus[last_turned_off_index] = 0
        GPIO.output(chillerPin[last_turned_off_index], chillerStatus[last_turned_off_index])
        update_actStream_table(now, chillerStatus[last_turned_off_index], last_turned_off_index+2)
        last_switch_time = time.time()
        if (last_turned_off_index + 1) == len(chillerStatus):
            last_turned_off_index = 0
        else:
            last_turned_off_index += 1
    return {"chillerStatus": chillerStatus,
            "last_turned_off_index": last_turned_off_index,
            "last_turned_on_index": last_turned_on_index,
            "last_switch_time": last_switch_time}

def switch_valve(valveFlag, valveStatus):
    if valveFlag != valveStatus:
        if valveFlag == 0:
            GPIO.output(valve1Pin, True)
            GPIO.output(valve2Pin, False)
        elif valveFlag == 1:
            GPIO.output(valve2Pin, True)
            GPIO.output(valve1Pin, False)
        valveStatus = valveFlag
    # time.sleep(120)
    return valveStatus

def update_db(outsideTemp, waterOutTemp, returnTemp, boilerStatus,
              chillerStatus, setPoint2, windSpeed):
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
            # sql2 = ("""UPDATE errTable SET err_T1=%s, err_T2=%s, err_Web=%s,
                    # err_GPIO=%s, err_DB=%s""" % (error_T1, error_T2,
                                                 # error_Web, error_GPIO,
                                                 # error_DB))
            cur.execute(sql1)
            # cur.execute(sql2)
    except MySQLdb.Error as e:
        print 'Error updating mainTable'
        logging.exception("Error updating table: %s" % e)

def update_actStream_table(timeStamp, status, TID):
    sql = "UPDATE actStream SET timeStamp=\"%s\", status=%s WHERE TID=%s" % (timeStamp, status, TID)
    try:
        with conn:
            cur = conn.cursor()
            cur.execute(sql)
    except MySQLdb.Error as e:
        logging.exception(sql)
        logging.exception("Error updating actStream table: %s" % e)

def update_sysStatus(error_T1, error_T2, error_DB, error_Web, error_GPIO):
    errData = [error_T1, error_T2, error_DB, error_Web, error_GPIO]
    try:
        with open("/var/www/sysStatus.txt", "w") as dataFile:
            for item in errData:
                dataFile.write("%s\n" % str(item))
    except IOError as e:
        print "Error opening file to write"
        logging.exception("Error opening file to write: %s" % e)

def sigterm_handler(_signo, _stack_frame):
    "When sysvinit sends the TERM signal, cleanup before exiting."
    print("Received signal {}, exiting...".format(_signo))
    destructor()
    sys.exit(0)

def destructor():
    if conn:
        conn.close()
    GPIO.cleanup()

signal.signal(signal.SIGTERM, sigterm_handler)

if __name__ == '__main__':
    breather_count = 0
    valveStatus = 0
    last_switch_time = 0
    last_turned_off_index, last_turned_on_index = 0, 0
    reset_db_values()
    try:
        while True:
            manage_system()
            errorDB = check_mysql()
            sensors_data = read_temperature_sensors()
            breather_count = blink_leds(sensors_data["waterOutTemp"],
                                        breather_count)
            db_data = read_values_from_db()
            web_data = get_data_from_web(db_data["mode"])
            setpoint = calculate_setpoint(web_data["outsideTemp"],
                                          db_data["setPoint2"],
                                          db_data["parameterX"])
            boiler_status = boiler_switcher(db_data["MO_B"],
                                            db_data["mode"],
                                            sensors_data["returnTemp"],
                                            setpoint["cur_eff_sp"],
                                            db_data["t1"],
                                            db_data["boilerStatus"])
            chiller_status = chillers_cascade_switcher(setpoint["cur_eff_sp"],
                                                       db_data["chillerStatus"],
                                                       sensors_data["returnTemp"],
                                                       db_data["t1"],
                                                       db_data["MO_C"],
                                                       db_data["CCT"],
                                                       db_data["mode"],
                                                       last_turned_off_index,
                                                       last_turned_on_index,
                                                       last_switch_time)
            last_switch_time = chiller_status["last_switch_time"]
            last_turned_off_index = chiller_status["last_turned_off_index"]
            last_turned_on_index = chiller_status["last_turned_on_index"]
            print chiller_status["chillerStatus"]
            valveStatus = switch_valve(setpoint["valveFlag"], valveStatus)
            update_db(web_data["outsideTemp"], sensors_data["waterOutTemp"],
                      sensors_data["returnTemp"], boiler_status,
                      chiller_status["chillerStatus"], setpoint["cur_eff_sp"],
                      web_data["windSpeed"])
    except KeyboardInterrupt:
        destructor()

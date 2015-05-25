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

log_formatter = logging.Formatter("%(asctime)s %(levelname)s:%(message)s",
                                  "%Y-%m-%d %H:%M:%S")
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(LOG_FILENAME)
file_handler.setFormatter(log_formatter)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)

root_logger.debug("Starting script")

# -----variables-----
water_out_temp = 00.00    #Temp sensor values. Also, the values that they...
return_temp = 00.00      #    ...fall back to if sensors are not available
boiler_status = 0        #ON = 1, OFF = 0
#valveStatus = 0
wind_chill_avg = 0
MO_B = 0                #Manual overrides. AUTO = 0, ON = 1, OFF = 2
t1 = 0                  #Threshold parameters
mode = 0                #Winter/Summer mode selector (0 -> Winter, 1 -> Summer)
power_mode = 0
temp_thresh = 80.00     #Threshold for breather LED color selection
led_breather = 22
# breather_count = 0
CCT = 5                 #Chiller Cascade Time
prev_eff_sp = 0
cur_eff_sp = 0
setpoint2 = 00.00
sp_min = 40.00
sp_max= 100.00
SYSTEMUP = "/var/www/systemUp.txt"
WINDCHILL_AVG = "/home/pi/Desktop/Chronos/windChillAvg.txt"
FIRMWARE_UPGRADE = "/home/pi/Desktop/Chronos/firmwareUpgrade.py"
# --------Arrays---------
chiller_status = [0 for i in xrange(4)]
MO_C = [0 for i in xrange(4)]
chiller_pin = [0 for i in xrange(4)]
# -----Set GPIO pins-----
boiler_pin = 20
chiller_pin[0] = 26
chiller_pin[1] = 16
chiller_pin[2] = 19
chiller_pin[3] = 5
valve1_pin = 6
valve2_pin = 12
led_red = 22
led_green = 23
led_blue = 24
#-----temp sensors-----
sensor_out_id = "28-00042d4367ff"
sensor_in_id = "28-00042c648eff"
#sensor_out_id = '28-00000677d162'
#sensor_in_id = '28-00000676e315'
# os.system('modprobe w1-gpio')
# os.system('modprobe w1-therm')

try:
    conn = MySQLdb.connect(host="localhost",
                           user="raspberry",
                           passwd="estrrado",
                           db="Chronos")
except MySQLdb.Error as e:
    root_logger.exception("Cannot connect to DB: %s" % e)
    conn = None
    destructor()
    sys.exit(1)

def set_gpio_pins():
    error_GPIO = 0
    try:
        # GPIO.setwarnings(False)
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(boiler_pin, GPIO.OUT)
        GPIO.setup(chiller_pin[0], GPIO.OUT)
        GPIO.setup(chiller_pin[1], GPIO.OUT)
        GPIO.setup(chiller_pin[2], GPIO.OUT)
        GPIO.setup(chiller_pin[3], GPIO.OUT)
        GPIO.setup(valve1_pin, GPIO.OUT)
        GPIO.setup(valve2_pin, GPIO.OUT)
        GPIO.output(boiler_pin, False)
        GPIO.output(chiller_pin[0], False)
        GPIO.output(chiller_pin[1], False)
        GPIO.output(chiller_pin[2], False)
        GPIO.output(chiller_pin[3], False)
        GPIO.output(valve1_pin, False)
        GPIO.output(valve2_pin, False)
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
        root_logger.exception("ErrorGPIO: %s" % e)
    return error_GPIO

def update_systemUp():
    try:
        with open(SYSTEMUP, "w") as dataFile:
            dataFile.write("ONLINE\n")
    except IOError as e:
        root_logger.exception("Can't write to systemUp.txt: %s" % e)

def reset_db_values():
    timeStamp = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with conn:
            cur = conn.cursor()
            sql1 = ("""UPDATE mainTable
                       SET boilerStatus=%s,
                           chiller1Status=%s,
                           chiller2Status=%s,
                           chiller3Status=%s,
                           chiller4Status=%s,
                           MO_B=%s,
                           MO_C1=%s,
                           MO_C2=%s,
                           MO_C3=%s,
                           MO_C4=%s,
                           powerMode=%s
                       ORDER BY LID
                       DESC LIMIT 1""" % (boiler_status,
                                          chiller_status[0],
                                          chiller_status[1],
                                          chiller_status[2],
                                          chiller_status[3],
                                          MO_B,
                                          MO_C[0],
                                          MO_C[1],
                                          MO_C[2],
                                          MO_C[3],
                                          power_mode))
            sql2 = ("""UPDATE actStream
                       SET timeStamp=\"%s\",
                           status=%s""" % (timeStamp, 0))
            cur.execute(sql1)
            cur.execute(sql2)
    except MySQLdb.Error as e:
        root_logger.exception("Error while resetting DB values: %s" % e)
        GPIO.output(led_red,True)
        time.sleep(0.7)
        GPIO.output(led_red,False)

def manage_system():
    "Check for shutdown, restart, etc."
    if power_mode == 10:
        subprocess.call(["reboot"])
    elif power_mode == 20:
        subprocess.call(["shutdown", "now"])
    elif power_mode == 2:
        subprocess.call(["python", FIRMWARE_UPGRADE])
        time.sleep(10)
    elif power_mode == 7:
        subprocess.call(["python", "/home/pi/Desktop/Chronos/Chronos_starter.py"])
        time.sleep(10)

def check_mysql():
    "Check if MySQL service is running."
    error_DB = 0
    try:
        with open("/var/run/mysqld/mysqld.pid") as pid_file:
            pid = int(pid_file.readline())
    except IOError as e:
        error_DB = 1
        root_logger.exception("Can't read mysql pid file: %s" % e)
        GPIO.output(led_red,True)
        time.sleep(0.7)
        GPIO.output(led_red,False)
    else:
        try:
            os.kill(pid, 0)
        except OSError:
            error_DB = 1
            root_logger.exception("MySQL is not running")
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
        # Divide by 1000 for proper decimal point
        temp = float(temp_string) / 1000.0
        # Convert to degF
        temp = temp * 9.0 / 5.0 + 32.0
        # Round temp to 2 decimal points
        temp = round(temp, 1)
        return temp

def read_temperature_sensors():
    "Read Temperature Sensors."
    error_T1 = 1
    error_T2 = 1
    DEVICE_DIR = "/home/pi/fake_sys/"
    for directory in os.listdir(DEVICE_DIR):
        if directory in (sensor_in_id, sensor_out_id):
            device_folder = os.path.join(DEVICE_DIR, directory)
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
                    root_logger.exception("Temp sensor error: %s" % e)
                    GPIO.output(led_red, True)
                    time.sleep(0.7)
                    GPIO.output(led_red, False)
                    with conn:
                        cur = conn.cursor()
                        sql = """SELECT returnTemp
                                 FROM mainTable
                                 ORDER BY LID
                                 DESC LIMIT 1"""
                        cur.execute(sql)
                        results = cur.fetchone()
                    return_temp = results[0]
            if device_id == sensor_out_id:
                water_out_temp = read_temp(device_file)
                error_T2 = 0
            elif device_id == sensor_in_id:
                return_temp = read_temp(device_file)
                error_T1 = 0
    return {"water_out_temp": water_out_temp, "return_temp": return_temp,
            "error_T1": error_T1, "error_T2": error_T2}

def blink_leds(water_out_temp, breather_count):
    if water_out_temp > temp_thresh:
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
            boiler_status = result[5]
            chiller_status = [result[6], result[7], result[8], result[9]]
            setpoint2 = result[10]
            parameterX = result[11]
            t1 = result[12]
            MO_B = result[13]
            MO_C = [result[14], result[15], result[16], result[17]]
            mode = result[18]
            power_mode = result[19]
            CCT = result[20]
    except MySQLdb.Error as e:
        root_logger.exception("Error fetching data from DB: %s" % e)
        GPIO.output(led_red,True) 
        time.sleep(0.7)
        GPIO.output(led_red,False)
    return {"boiler_status": boiler_status,
            "chillerStatus": chiller_status,
            "setpoint2": setpoint2,
            "parameterX": parameterX,
            "t1": t1,
            "MO_B": MO_B,
            "MO_C": MO_C,
            "mode": mode,
            "power_mode": power_mode,
            "CCT": CCT*60}

def get_data_from_web(mode):
    "Parsing windChill and windSpeed from wx.thomaslivestock.com."
    error_Web = 0
    try:
        content = urllib2.urlopen('http://wx.thomaslivestock.com')
    except IOError, HTTPError:
        root_logger.exception("""Unable to get data from website.
                             Reading previous value from DB.""")
        error_Web = 1
        GPIO.output(led_red, True)
        time.sleep(0.7)
        GPIO.output(led_red, False)
        try:
            with conn:
                cur = conn.cursor()
                sql = """SELECT outsideTemp, windSpeed
                         FROM mainTable
                         ORDER BY LID
                         DESC LIMIT 1"""
                cur.execute(sql)
                results = cur.fetchone()
                outsideTemp = results[0]
                windSpeed = results[1]
        except MySQLdb.Error:
            root_logger.exception("""Unable to get value from DB.
                                 Reverting to default value of 65 deg F""")
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
        # Wind speed
        node = tree.xpath(
            "/html/body/table/tr[6]/td[2]/font/strong/font/small/text()")
        wind_speed = float(node[0].split()[2])
    return {"outsideTemp": outsideTemp,
            "windSpeed": wind_speed,
            "error_Web": error_Web}

def calculate_setpoint(outsideTemp, setpoint2, parameterX):
    "Calculate setpoint from windChill."
    windChill = int(outsideTemp)
    sql = """SELECT AVG(outsideTemp)
             FROM mainTable
             WHERE logdatetime > DATE_SUB(CURDATE(), INTERVAL 96 HOUR)
             AND MODE = (SELECT MODE FROM mainTable
                         ORDER BY LID DESC
                         LIMIT 1)
             ORDER BY LID DESC
             LIMIT 5760"""
    try:
        with conn:
            cur = conn.cursor()
            cur.execute(sql)
            result = cur.fetchone()
            wind_chill_avg = result[0]
    except MySQLdb.Error as e:
        root_logger.exception("Unable to get value from DB: %s" % e)
    # try:
    #     with open(WINCHILL_AVG) as windChillFile:
    #         buf = windChillFile.read(3)
    #         index = buf.find(".")
    #         wind_chill_avg = int(buf[0:index])
    # except IOError as e:
    #     root_logger.exception("Unable to open file to read: %s" % e)
    if windChill < 11:
        setpoint2 = 100
    else:
        try:
            with conn:
                cur = conn.cursor()
                sql = ("""SELECT setPoint
                          FROM SetpointLookup
                          WHERE windChill = %s""" % windChill)
                cur.execute(sql)
                results = cur.fetchone()
                setpoint2 = results[0]
        except MySQLdb.Error as e:
            root_logger.exception("Setpoint error: %s" % e)
    if wind_chill_avg < 71:
        setpointOffset = 0
    else:
        try:
            with conn:
                cur = conn.cursor()
                sql = ("""SELECT setPointOffset
                          FROM SetpointLookup
                          WHERE avgWindChill = %s""" % wind_chill_avg)
                cur.execute(sql)
                results = cur.fetchone()
                setpointOffset = results[0]
        except MySQLdb.Error as e:
            setpointOffset = 0
            root_logger.exception("Setpoint error: %s" % e)
    setpoint2 -= setpointOffset
    cur_eff_sp = setpoint2 + parameterX
    #constrain effective setpoint
    try:
        with open("/usr/local/bin/spMin.txt") as spMinFile:
            buf = spMinFile.readline()
            sp_min = float(buf)
    except IOError as e:
        root_logger.exception("Unable to open spMin.txt to read: %s" % e)
    try:
        with open("/usr/local/bin/spMax.txt") as spMaxFile:
            buf = spMaxFile.readline()
            sp_max = float(buf)
    except IOError as e:
        root_logger.exception("Unable to open spMax.txt to read: %s" % e)
    if cur_eff_sp > sp_max:
        cur_eff_sp = sp_max
    elif cur_eff_sp < sp_min:
        cur_eff_sp = sp_min
    # if cur_eff_sp != prev_eff_sp:
    try:
        with open("/usr/local/bin/sp.txt", "w") as dataFile:
            dataFile.write(str(cur_eff_sp))
    except IOError as e:
        root_logger.exception("Error opening sp.txt: %s" % e)
    return cur_eff_sp

def boiler_switcher(MO_B, mode, return_temp, cur_eff_sp, t1, boiler_status):
    now = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    if MO_B == 0:
        if boiler_status == 0 and mode == 0 and return_temp <= (cur_eff_sp - t1):
            boiler_status = 1
            GPIO.output(boiler_pin, True)
            update_actStream_table(now, boiler_status, 1)
        elif boiler_status == 1 and mode == 0 and return_temp > (cur_eff_sp + t1):
            boiler_status = 0
            GPIO.output(boiler_pin, False)
            update_actStream_table(now, boiler_status, 1)
        elif boiler_status == 1 and mode == 1:
            boiler_status = 0
            GPIO.output(boiler_pin, False)
            update_actStream_table(now, boiler_status, 1)
    elif MO_B == 1 and boiler_status == 0:
        boiler_status = 1
        GPIO.output(boiler_pin, True)
        update_actStream_table(now, boiler_status, 1)
    elif MO_B == 2 and boiler_status == 1:
        boiler_status = 0
        GPIO.output(boiler_pin, False)
        update_actStream_table(now, boiler_status, 1)
    return boiler_status

def chillers_cascade_switcher(cur_eff_sp, chiller_status, return_temp, t1, MO_C, CCT, mode, last_turned_off_index,
                              last_turned_on_index, last_switch_time):
    timeGap = time.time() - last_switch_time
    now = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    # Manual override
    skip_indexes = []
    for i, MO_C_item in enumerate(MO_C):
        if MO_C_item == 1:
            if chiller_status[i] == 0:
                chiller_status[i] = 1
                GPIO.output(chiller_pin[i], chiller_status[i])
                update_actStream_table(now, chiller_status[i], i+2)
            skip_indexes.append(i)
        elif MO_C_item == 2:
            if chiller_status[i] == 1:
                chiller_status[i] = 0
                GPIO.output(chiller_pin[i], chiller_status[i])
                update_actStream_table(now, chiller_status[i], i+2)
            skip_indexes.append(i)
    # Turn on chillers
    if (return_temp >= (cur_eff_sp + t1)
        and timeGap >= CCT
        and mode == 1
        and 0 in chiller_status
        and last_turned_on_index not in skip_indexes):
        chiller_status[last_turned_on_index] = 1
        GPIO.output(chiller_pin[last_turned_on_index], chiller_status[last_turned_on_index])
        update_actStream_table(now, chiller_status[last_turned_on_index], last_turned_on_index+2)
        last_switch_time = time.time()
        if (last_turned_on_index + 1) == len(chiller_status):
            last_turned_on_index = 0
        else:
            last_turned_on_index += 1
    # Turn off chillers
    elif (return_temp < (cur_eff_sp - t1)
          and timeGap >= CCT
          and mode == 1
          and 1 in chiller_status
          and last_turned_off_index not in skip_indexes):
        chiller_status[last_turned_off_index] = 0
        GPIO.output(chiller_pin[last_turned_off_index], chiller_status[last_turned_off_index])
        update_actStream_table(now, chiller_status[last_turned_off_index], last_turned_off_index+2)
        last_switch_time = time.time()
        if (last_turned_off_index + 1) == len(chiller_status):
            last_turned_off_index = 0
        else:
            last_turned_off_index += 1
    # Turn off chillers when winter
    elif (mode == 0
          and 1 in chiller_status
          and last_turned_off_index not in skip_indexes):
        chiller_status[last_turned_off_index] = 0
        GPIO.output(chiller_pin[last_turned_off_index], chiller_status[last_turned_off_index])
        update_actStream_table(now, chiller_status[last_turned_off_index], last_turned_off_index+2)
        last_switch_time = time.time()
        if (last_turned_off_index + 1) == len(chiller_status):
            last_turned_off_index = 0
        else:
            last_turned_off_index += 1
    return {"chiller_status": chiller_status,
            "last_turned_off_index": last_turned_off_index,
            "last_turned_on_index": last_turned_on_index,
            "last_switch_time": last_switch_time}

def switch_valve(mode, valveStatus):
    if mode == 0 and valveStatus != mode:
        GPIO.output(valve1_pin, True)
        GPIO.output(valve2_pin, False)
    elif mode == 1 and valveStatus != mode:
        GPIO.output(valve2_pin, True)
        GPIO.output(valve1_pin, False)
    valveStatus = mode
    # time.sleep(120)
    return valveStatus

def update_db(outsideTemp, water_out_temp, return_temp, boiler_status,
              chiller_status, setpoint2, windSpeed):
    try:
        with conn:
            cur = conn.cursor()
            sql1 = ("""UPDATE mainTable
                       SET outsideTemp=%s,
                           waterOutTemp=%s,
                           returnTemp=%s,
                           boilerStatus=%s,
                           chiller1Status=%s,
                           chiller2Status=%s,
                           chiller3Status=%s,
                           chiller4Status=%s,
                           setPoint2=%s,
                           windSpeed=%s
                       ORDER BY LID
                       DESC LIMIT 1""" % (outsideTemp,
                                          water_out_temp,
                                          return_temp,
                                          boiler_status,
                                          chiller_status[0],
                                          chiller_status[1],
                                          chiller_status[2],
                                          chiller_status[3],
                                          setpoint2,
                                          windSpeed))
            # sql2 = ("""UPDATE errTable SET err_T1=%s, err_T2=%s, err_Web=%s,
                    # err_GPIO=%s, err_DB=%s""" % (error_T1, error_T2,
                                                 # error_Web, error_GPIO,
                                                 # error_DB))
            cur.execute(sql1)
            # cur.execute(sql2)
    except MySQLdb.Error as e:
        root_logger.exception("Error updating table: %s" % e)

def update_actStream_table(timeStamp, status, TID):
    sql = "UPDATE actStream SET timeStamp=\"%s\", status=%s WHERE TID=%s" % (timeStamp, status, TID)
    try:
        with conn:
            cur = conn.cursor()
            cur.execute(sql)
    except MySQLdb.Error as e:
        root_logger.exception(sql)
        root_logger.exception("Error updating actStream table: %s" % e)

def update_sysStatus(error_T1, error_T2, error_DB, error_Web, error_GPIO):
    errData = [error_T1, error_T2, error_DB, error_Web, error_GPIO]
    try:
        with open("/var/www/sysStatus.txt", "w") as dataFile:
            for item in errData:
                dataFile.write("%s\n" % str(item))
    except IOError as e:
        root_logger.exception("Error opening file to write: %s" % e)

def sigterm_handler(_signo, _stack_frame):
    "When sysvinit sends the TERM signal, cleanup before exiting."
    destructor()
    sys.exit(0)

def destructor():
    if conn:
        conn.close()
    with open(SYSTEMUP, "w") as dataFile:
        dataFile.write("OFFLINE\n")
    GPIO.cleanup()

signal.signal(signal.SIGTERM, sigterm_handler)

if __name__ == '__main__':
    breather_count = 0
    valveStatus = 0
    last_switch_time = 0
    last_turned_off_index, last_turned_on_index = 0, 0
    update_systemUp()
    set_gpio_pins()
    reset_db_values()
    try:
        while True:
            manage_system()
            errorDB = check_mysql()
            sensors_data = read_temperature_sensors()
            breather_count = blink_leds(sensors_data["water_out_temp"],
                                        breather_count)
            db_data = read_values_from_db()
            web_data = get_data_from_web(db_data["mode"])
            setpoint = calculate_setpoint(web_data["outsideTemp"],
                                          db_data["setpoint2"],
                                          db_data["parameterX"])
            boiler_status = boiler_switcher(db_data["MO_B"],
                                            db_data["mode"],
                                            sensors_data["return_temp"],
                                            setpoint,
                                            db_data["t1"],
                                            db_data["boiler_status"])
            chiller_status = chillers_cascade_switcher(setpoint,
                                                       db_data["chiller_status"],
                                                       sensors_data["return_temp"],
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
            valveStatus = switch_valve(db_data["mode"], valveStatus)
            update_db(web_data["outsideTemp"], sensors_data["water_out_temp"],
                      sensors_data["return_temp"], boiler_status,
                      chiller_status["chiller_status"], setpoint,
                      web_data["windSpeed"])
    except KeyboardInterrupt:
        destructor()

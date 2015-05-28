#!/usr/bin/env python

import time
import logging
import os
import MySQLdb
import urllib2
import subprocess
import signal
import sys
import RPi.GPIO as GPIO
from lxml import etree
from logging.handlers import TimedRotatingFileHandler

# Constants
LOG_FILENAME = "/var/log/chronos.log"
SYSTEMUP = "/var/www/chronosreal/systemUp.txt"
FIRMWARE_UPGRADE = "/home/pi/Desktop/Chronos/firmwareUpgrade.py"
# Set GPIO pins
boiler_pin = 20
chiller_pin = [0]*4
chiller_pin[0] = 26
chiller_pin[1] = 16
chiller_pin[2] = 19
chiller_pin[3] = 5
valve1_pin = 6
valve2_pin = 12
led_breather = 22
led_red = 22
led_green = 23
led_blue = 24
# Temp sensors
sensor_out_id = "28-00042d4367ff"
sensor_in_id = "28-00042c648eff"
#sensor_out_id = '28-00000677d162'
#sensor_in_id = '28-00000676e315'
# os.system('modprobe w1-gpio')
# os.system('modprobe w1-therm')

# Configuring loggging
log_formatter = logging.Formatter("%(asctime)s %(levelname)s:%(message)s",
                                  "%Y-%m-%d %H:%M:%S")
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
rotate_logs_handler = TimedRotatingFileHandler(LOG_FILENAME, "midnight")
rotate_logs_handler.setFormatter(log_formatter)
root_logger.addHandler(console_handler)
root_logger.addHandler(rotate_logs_handler)

root_logger.debug("Starting script")

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
        GPIO.output(led_red, True)
        time.sleep(0.7)
        GPIO.output(led_red, False)
        root_logger.exception("ErrorGPIO: %s" % e)
    return error_GPIO


def update_systemUp():
    try:
        with open(SYSTEMUP, "w") as dataFile:
            dataFile.write("ONLINE\n")
    except IOError as e:
        root_logger.exception("Can't write to systemUp.txt: %s" % e)


def init_values():
    try:
        with conn:
            cur = conn.cursor()
            sql = """SELECT status, timeStamp
                     FROM actStream"""
            cur.execute(sql)
            result = cur.fetchall()
            chiller_status = [result[1][0], result[2][0], result[3][0], result[4][0]]
            time_stamps = [result[1][1], result[2][1], result[3][1], result[4][1]]
            last_switch_time = max(time_stamps)
            last_switched_chiller = time_stamps.index(last_switch_time)
            if chiller_status[last_switched_chiller] == 1:
                last_turned_on_index = last_switched_chiller
                # This is ugly but works (I hope). To find last turned off chiller
                # we need find first turned on chiller. Last turned off chiller
                # will be on the left of that chiller.
                # So here we are filtering chillers which are turned on
                ones = [time_stamps[i] for i, chiller in enumerate(chiller_status) if chiller == 1]
                if ones:
                    # Here we are finding index of the chiller which has
                    # a minimal timestamp. Than we move to the left
                    # of it deducting 1.
                    last_turned_off_index = time_stamps.index(min(ones)) - 1
            elif chiller_status[last_switched_chiller] == 0:
                last_turned_off_index = last_switched_chiller
                zeroes = [time_stamps[i] for i, chiller in enumerate(chiller_status) if chiller == 0]
                if zeroes:
                    last_turned_on_index = time_stamps.index(min(zeroes)) - 1
            # This need when actStream table is resetted. 
            # If there is one timestamp for all chillers then table is resetted.
            if len(set(time_stamps)) == 1:
                last_turned_off_index, last_turned_on_index = -1, -1
    except MySQLdb.Error as e:
        root_logger.exception("DB error: %s" % e)
        GPIO.output(led_red, True)
        time.sleep(0.7)
        GPIO.output(led_red, False)
    return {"last_turned_on_index": last_turned_on_index,
            "last_turned_off_index": last_turned_off_index,
            "last_switch_time": time.mktime(last_switch_time.timetuple())}


def manage_system(power_mode):
    "Check for shutdown, restart, etc."
    if power_mode == 10:
        subprocess.call(["reboot"])
    elif power_mode == 20:
        subprocess.call(["shutdown", "now"])
    elif power_mode == 2:
        subprocess.call(["python", FIRMWARE_UPGRADE])
        time.sleep(10)
    elif power_mode == 7:
        subprocess.call(
            ["python", "/home/pi/Desktop/Chronos/Chronos_starter.py"])
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
        GPIO.output(led_red, True)
        time.sleep(0.7)
        GPIO.output(led_red, False)
    else:
        try:
            os.kill(pid, 0)
        except OSError:
            error_DB = 1
            root_logger.exception("MySQL is not running")
            GPIO.output(led_red, True)
            time.sleep(0.7)
            GPIO.output(led_red, False)
            destructor()
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
    water_out_temp = 00.00
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
                pass
            try:
                with open(device_file) as content:
                    temp_raw = content.readlines()
            except IOError as e:
                root_logger.exception("Temp sensor error: %s" % e)
                GPIO.output(led_red, True)
                time.sleep(0.7)
                GPIO.output(led_red, False)
                try:
                    with conn:
                        cur = conn.cursor()
                        sql = """SELECT returnTemp
                                 FROM mainTable
                                 ORDER BY LID
                                 DESC LIMIT 1"""
                        cur.execute(sql)
                        results = cur.fetchone()
                    return_temp = results[0]
                except MySQLdb.Error:
                    return_temp = 00.00
            if device_id == sensor_out_id:
                water_out_temp = read_temp(device_file)
                error_T2 = 0
            elif device_id == sensor_in_id:
                return_temp = read_temp(device_file)
                error_T1 = 0
    return {"water_out_temp": water_out_temp,
            "return_temp": return_temp,
            "errors": [error_T1, error_T2]}


def blink_leds(water_out_temp, breather_count):
    temp_thresh = 80.00  # Threshold for breather LED color selection
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
            sql1 = """SELECT setPoint2, parameterX, t1, mode, CCT
                      FROM mainTable ORDER BY LID DESC LIMIT 1"""
            cur.execute(sql1)
            result1 = cur.fetchone()
            setpoint2 = result1[0]
            parameterX = result1[1]
            t1 = result1[2]
            mode = result1[3]
            CCT = result1[4]
            sql2 = "SELECT status, MO FROM actStream"
            cur.execute(sql2)
            result2 = cur.fetchall()
            boiler_status = result2[0][0]
            chiller_status = [result2[1][0], result2[2][0], result2[3][0], result2[4][0]]
            MO_B = result2[0][1]
            MO_C = [result2[1][1], result2[2][1], result2[3][1], result2[4][1]]
            # power_mode = result[19]
    except MySQLdb.Error as e:
        boiler_status = 0  # ON = 1, OFF = 0
        chiller_status = [0]*4
        setpoint2 = 00.00
        parameterX = 0
        t1 = 0
        MO_B = 0  # Manual overrides. AUTO = 0, ON = 1, OFF = 2
        MO_C = [0]*4
        mode = 0  # Winter/Summer mode selector (0 -> Winter, 1 -> Summer)
        power_mode = 0
        CCT = 5  # Chiller Cascade Time
        root_logger.exception("Error fetching data from DB: %s" % e)
        GPIO.output(led_red, True)
        time.sleep(0.7)
        GPIO.output(led_red, False)
    return {"boiler_status": boiler_status,
            "chiller_status": chiller_status,
            "setpoint2": setpoint2,
            "parameterX": parameterX,
            "t1": t1,
            "MO_B": MO_B,
            "MO_C": MO_C,
            "mode": mode,
            # "power_mode": power_mode,
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
                outside_temp = results[0]
                wind_speed = results[1]
        except MySQLdb.Error:
            root_logger.exception("""Unable to get value from DB.
                                 Reverting to default value of 65 deg F""")
            outside_temp = 65.00
            wind_speed = 0.00
    else:
        html = content.read()
        tree = etree.HTML(html)
        # Wind chill
        if mode == 0:
            node = tree.xpath(
                "/html/body/table/tr[10]/td[2]/font/strong/font/small/text()")
        # Temperature
        elif mode == 1:
            node = tree.xpath(
                "/html/body/table/tr[3]/td[2]/font/strong/small/font/text()")
        outTemp = node[0].split(u"\xb0F")[0]
        outside_temp = float(outTemp)
        # Wind speed
        node = tree.xpath(
            "/html/body/table/tr[6]/td[2]/font/strong/font/small/text()")
        wind_speed = float(node[0].split()[2])
    return {"outside_temp": outside_temp,
            "windSpeed": wind_speed,
            "error_Web": error_Web}


def calculate_setpoint(outside_temp, setpoint2, parameterX, mode):
    "Calculate setpoint from windChill."
    wind_chill = int(outside_temp)
    try:
        with conn:
            cur = conn.cursor()
            sql = ("""SELECT AVG(outsideTemp)
                      FROM mainTable
                      WHERE logdatetime > DATE_SUB(CURDATE(), INTERVAL 96 HOUR)
                      AND mode = %s
                      ORDER BY LID DESC
                      LIMIT 5760""" % mode)
            cur.execute(sql)
            result = cur.fetchone()
            wind_chill_avg = result[0]
    except MySQLdb.Error as e:
        wind_chill_avg = 0
        root_logger.exception("Unable to get value from DB: %s" % e)
    if wind_chill < 11:
         baseline_setpoint = 100
    else:
        try:
            with conn:
                cur = conn.cursor()
                sql = ("""SELECT setPoint
                          FROM SetpointLookup
                          WHERE windChill = %s""" % wind_chill)
                cur.execute(sql)
                results = cur.fetchone()
                baseline_setpoint = results[0]
        except MySQLdb.Error as e:
            root_logger.exception("Setpoint error: %s" % e)
    if wind_chill_avg < 71:
        temperature_history_adjsutment = 0
    else:
        try:
            with conn:
                cur = conn.cursor()
                sql = ("""SELECT setPointOffset
                          FROM SetpointLookup
                          WHERE avgWindChill = %s""" % wind_chill_avg)
                cur.execute(sql)
                results = cur.fetchone()
                temperature_history_adjsutment = results[0]
        except MySQLdb.Error as e:
            temperature_history_adjsutment = 0
            root_logger.exception("Setpoint error: %s" % e)
    tha_setpoint = baseline_setpoint + temperature_history_adjsutment
    effective_setpoint = tha_setpoint + parameterX
    # constrain effective setpoint
    try:
        with open("/usr/local/bin/spMin.txt") as spMinFile:
            buf = spMinFile.readline()
            sp_min = float(buf)
    except IOError as e:
        sp_min = 40.00
        root_logger.exception("Unable to open spMin.txt to read: %s" % e)
    try:
        with open("/usr/local/bin/spMax.txt") as spMaxFile:
            buf = spMaxFile.readline()
            sp_max = float(buf)
    except IOError as e:
        sp_max = 100.00
        root_logger.exception("Unable to open spMax.txt to read: %s" % e)
    if effective_setpoint > sp_max:
        effective_setpoint = sp_max
    elif effective_setpoint < sp_min:
        effective_setpoint = sp_min
    try:
        with open("/usr/local/bin/sp.txt", "w") as dataFile:
            dataFile.write(str(effective_setpoint))
    except IOError as e:
        root_logger.exception("Error opening sp.txt: %s" % e)
    return {"effective_setpoint": effective_setpoint,
            "tha_setpoint": tha_setpoint}


def boiler_switcher(MO_B, mode, return_temp, effective_setpoint, t1, boiler_status):
    new_boiler_status = boiler_status
    if MO_B == 0:
        if (new_boiler_status == 0
                and mode == 0
                and return_temp <= (effective_setpoint - t1)):
            new_boiler_status = 1
            GPIO.output(boiler_pin, True)
            update_actStream_table(new_boiler_status, None, True)
        elif (new_boiler_status == 1
                and mode == 0
                and return_temp > (effective_setpoint + t1)):
            new_boiler_status = 0
            GPIO.output(boiler_pin, False)
            update_actStream_table(new_boiler_status, None, True)
        elif new_boiler_status == 1 and mode == 1:
            new_boiler_status = 0
            GPIO.output(boiler_pin, False)
            update_actStream_table(new_boiler_status, None, True)
    elif MO_B == 1 and new_boiler_status == 0:
        new_boiler_status = 1
        GPIO.output(boiler_pin, True)
        update_actStream_table(new_boiler_status, None, True)
    elif MO_B == 2 and new_boiler_status == 1:
        new_boiler_status = 0
        GPIO.output(boiler_pin, False)
        update_actStream_table(new_boiler_status, None, True)
    return new_boiler_status


def chillers_cascade_switcher(effective_setpoint, chiller_status, return_temp,
                              t1, MO_C, CCT, mode, last_turned_off_index,
                              last_turned_on_index, last_switch_time):
    time_gap = time.time() - last_switch_time
    # Manual override
    skip_indexes = []
    new_chiller_status = chiller_status[:]
    for i, MO_C_item in enumerate(MO_C):
        if MO_C_item == 1:
            if new_chiller_status[i] == 0:
                new_chiller_status[i] = 1
                GPIO.output(chiller_pin[i], new_chiller_status[i])
                update_actStream_table(new_chiller_status[i], i)
            skip_indexes.append(i)
        elif MO_C_item == 2:
            if new_chiller_status[i] == 1:
                new_chiller_status[i] = 0
                GPIO.output(chiller_pin[i], new_chiller_status[i])
                update_actStream_table(new_chiller_status[i], i)
            skip_indexes.append(i)
    # Turn on chillers
    if (return_temp >= (effective_setpoint + t1)
            and time_gap >= CCT
            and mode == 1
            and 0 in new_chiller_status
            and last_turned_on_index not in skip_indexes):
        # root_logger.debug((last_turned_on_index, last_turned_off_index))
        if (last_turned_on_index + 1) == len(new_chiller_status):
            last_turned_on_index = 0
        else:
            last_turned_on_index += 1
        new_chiller_status[last_turned_on_index] = 1
        GPIO.output(chiller_pin[last_turned_on_index],
                    new_chiller_status[last_turned_on_index])
        update_actStream_table(new_chiller_status[last_turned_on_index],
                               last_turned_on_index)
        last_switch_time = time.time()
    # Turn off chillers
    elif (return_temp < (effective_setpoint - t1)
            and time_gap >= CCT
            and mode == 1
            and 1 in new_chiller_status
            and last_turned_off_index not in skip_indexes):
        if (last_turned_off_index + 1) == len(new_chiller_status):
            last_turned_off_index = 0
        else:
            last_turned_off_index += 1
        new_chiller_status[last_turned_off_index] = 0
        GPIO.output(chiller_pin[last_turned_off_index],
                    new_chiller_status[last_turned_off_index])
        update_actStream_table(new_chiller_status[last_turned_off_index],
                               last_turned_off_index)
        last_switch_time = time.time()
    # Turn off chillers when winter
    elif (mode == 0
            and 1 in new_chiller_status
            and last_turned_off_index not in skip_indexes):
        if (last_turned_off_index + 1) == len(new_chiller_status):
            last_turned_off_index = 0
        else:
            last_turned_off_index += 1
        new_chiller_status[last_turned_off_index] = 0
        GPIO.output(chiller_pin[last_turned_off_index],
                    new_chiller_status[last_turned_off_index])
        update_actStream_table(new_chiller_status[last_turned_off_index],
                               last_turned_off_index)
        last_switch_time = time.time()
    # if chiller manually overrided then skip it
    elif (last_turned_on_index in skip_indexes
          and 0 in new_chiller_status):
        if (last_turned_on_index + 1) == len(new_chiller_status):
            last_turned_on_index = 0
        else:
            last_turned_on_index += 1
    elif (last_turned_off_index in skip_indexes
          and 1 in new_chiller_status):
        if (last_turned_off_index + 1) == len(new_chiller_status):
            last_turned_off_index = 0
        else:
            last_turned_off_index += 1
    string = ", ".join([str(i) for i in new_chiller_status])
    root_logger.debug("Chillers: %s; time gap: %d; last switch time: %s" % (string,
                                                                            time_gap,
                                                                            time.strftime("%H:%M:%S", time.localtime(last_switch_time))))
    return {"chiller_status": new_chiller_status,
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


def update_db(outside_temp, water_out_temp, return_temp, boiler_status,
              chiller_status, setpoint2, wind_speed):
    try:
        with conn:
            cur = conn.cursor()
            sql1 = "SELECT MO FROM actStream"
            cur.execute(sql1)
            MO = cur.fetchall()
            MO = [item for sublist in MO for item in sublist]
            data = [time.strftime("%Y-%m-%d %H:%M:%S")]
            args = [outside_temp, water_out_temp, return_temp, boiler_status, chiller_status[0],
                    chiller_status[1], chiller_status[2], chiller_status[3], setpoint2]
            data.extend(args)
            string1 = ",".join(["\"%s\"" % i for i in data])
            string2 = ",".join(["\"%s\"" % i for i in MO])
            sql2 = ("""INSERT INTO mainTable (logdatetime,
                                              outsideTemp,
                                              waterOutTemp,
                                              returnTemp,
                                              boilerStatus,
                                              chiller1Status,
                                              chiller2Status,
                                              chiller3Status,
                                              chiller4Status,
                                              setPoint2,
                                              parameterX,
                                              t1,
                                              MO_B,
                                              MO_C1,
                                              MO_C2,
                                              MO_C3,
                                              MO_C4,
                                              mode,
                                              powerMode,
                                              CCT,
                                              windSpeed)
                       SELECT %s,parameterX,t1,%s,mode,powerMode,CCT,\"%s\"
                       FROM mainTable
                       ORDER BY LID DESC
                       LIMIT 1""" % (string1,
                                     string2,
                                     wind_speed))
            cur.execute(sql2)
    except MySQLdb.Error as e:
        root_logger.exception("Error updating table: %s" % e)


def update_actStream_table(status, chiller_id, boiler=False):
    if boiler:
        tid = 1
    else:
        tid = chiller_id + 2
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    sql = ("""UPDATE actStream
              SET timeStamp=\"%s\",
                  status=%s
              WHERE TID=%s""" % (now, status, tid))
    try:
        with conn:
            cur = conn.cursor()
            cur.execute(sql)
    except MySQLdb.Error as e:
        root_logger.exception("Error updating actStream table: %s" % e)


def update_sysStatus(error_sensor, error_DB, error_Web, error_GPIO):
    errData = [error_sensor[0], error_sensor[1], error_DB, error_Web, error_GPIO]
    try:
        with open("/var/www/sysStatus.txt", "w") as dataFile:
            for item in errData:
                dataFile.write("%s\n" % str(item))
    except IOError as e:
        root_logger.exception("Error opening file to write: %s" % e)
    try:
        with conn:
            cur = conn.cursor()
            sql = ("""UPDATE errTable
                      SET err_T1=%s,
                          err_T2=%s,
                          err_Web=%s,
                          err_GPIO=%s""" % (error_sensor[0],
                                            error_sensor[1],
                                            error_Web,
                                            error_GPIO))
            cur.execute(sql)
    except MySQLdb.Error as e:
        root_logger.exception("Error updating actStream table: %s" % e)            


def sigterm_handler():
    "When sysvinit sends the TERM signal, cleanup before exiting."
    destructor()
    sys.exit(0)


def destructor():
    if conn:
        time.sleep(2)
        conn.close()
    with open(SYSTEMUP, "w") as dataFile:
        dataFile.write("OFFLINE\n")
    GPIO.cleanup()

signal.signal(signal.SIGTERM, sigterm_handler)

if __name__ == '__main__':
    breather_count = 0
    valveStatus = 0
    # last_switch_time = 0
    # last_turned_off_index, last_turned_on_index = 0, 0
    timer = 0 
    update_systemUp()
    error_GPIO = set_gpio_pins()
    init_values = init_values()
    last_switch_time = init_values["last_switch_time"]
    last_turned_on_index = init_values["last_turned_on_index"]
    last_turned_off_index = init_values["last_turned_off_index"]
    try:
        while True:
            error_DB = check_mysql()
            sensors_data = read_temperature_sensors()
            breather_count = blink_leds(sensors_data["water_out_temp"],
                                        breather_count)
            db_data = read_values_from_db()
            web_data = get_data_from_web(db_data["mode"])
            setpoint = calculate_setpoint(web_data["outside_temp"],
                                          db_data["setpoint2"],
                                          db_data["parameterX"],
                                          db_data["mode"])
            boiler_status = boiler_switcher(db_data["MO_B"],
                                            db_data["mode"],
                                            sensors_data["return_temp"],
                                            setpoint["effective_setpoint"],
                                            db_data["t1"],
                                            db_data["boiler_status"])
            chiller_status = chillers_cascade_switcher(setpoint["effective_setpoint"],
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
            # Update db every minute
            if time.time() - timer >= 60:
                update_db(web_data["outside_temp"],
                          sensors_data["water_out_temp"],
                          sensors_data["return_temp"],
                          boiler_status,
                          chiller_status["chiller_status"],
                          setpoint["tha_setpoint"],
                          web_data["windSpeed"])
                timer = time.time()
            update_sysStatus(sensors_data["errors"],
                             error_DB,
                             web_data["error_Web"],
                             error_GPIO)
            # manage_system(db_data["power_mode"])
    except KeyboardInterrupt:
        destructor()

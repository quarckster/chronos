#!/usr/bin/env python

import MySQLdb
import datetime
import logging
import time
import os
import subprocess

CHRONOS_MAIN = "/home/pi/Desktop/Chronos/Chronos_main.py"
CHRONOS_STARTER = "/home/pi/chronosqemu/Python/Chronos_starter.py"
SYSTEMUP = "/var/www/systemUp.txt"
SYSTEMDOWN = "/var/www/systemDown.txt"
LOG_FILENAME = "/home/pi/chronosqemu/Python/log_Chronos_sec.out"
LED_TRIAL = "/home/pi/chronosqemu/Python/led_trial2.py"
LED_STARTER = "/home/pi/chronosqemu/Python/led_starter.py"
WIND_CHILL = "/home/pi/chronosqemu/Python/windChillAvg.txt"
logging.basicConfig(filename=LOG_FILENAME,
                    level=logging.ERROR,
                    format="%(asctime)s %(levelname)s:%(message)s")


def get_count():
    try:
        with open(SYSTEMUP) as readfile:
            inputstr = readfile.readlines()
        count = int(inputstr[1])
    except (IOError, IndexError) as e:
        print "FileReadError: %s" % e
        logging.exception("FileReadError: %s" % e)
        count = 0
    finally:
        return count


def db_queries():
    try:
        conn = MySQLdb.connect(host="localhost",
                                    user="raspberry",
                                    passwd="estrrado",
                                    db="Chronos")
    except MySQLdb.Error as e:
        print "Can't connect to database: %s" % e
        logging.exception("DBConnectionError: %s" % e)
    else:
        logdate = time.strftime("%Y-%m-%d %H:%M:00")
        sql1 = ("INSERT INTO mainTable (logdatetime,outsideTemp,waterOutTemp,"
                "returnTemp,boilerStatus,chiller1Status,chiller2Status,"
                "chiller3Status,chiller4Status,setPoint2,parameterX,t1,MO_B,"
                "MO_C1,MO_C2,MO_C3,MO_C4,mode,powerMode,CCT,windSpeed) SELECT "
                "\"%s\",outsideTemp,waterOutTemp,returnTemp,boilerStatus,"
                "chiller1Status,chiller2Status,chiller3Status,chiller4Status,"
                "setPoint2,parameterX,t1,MO_B,MO_C1,MO_C2,MO_C3,MO_C4,mode,"
                "powerMode,CCT,windSpeed FROM mainTable ORDER BY LID DESC "
                "LIMIT 1" % logdate)
        sql2 = ("SELECT outsideTemp FROM mainTable WHERE logdatetime > "
                "DATE_SUB(CURDATE(), INTERVAL 96 HOUR) AND mode = (SELECT mode"
                " FROM mainTable ORDER BY LID DESC LIMIT 1) ORDER BY LID DESC"
                " LIMIT 5760")
        with conn:
            cur = conn.cursor()
            cur.execute(sql1)
            cur.execute(sql2)
            results = cur.fetchall()
        return results


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


def update_systemUp(count):
    if is_process_exists(CHRONOS_MAIN):
        error_system = "ONLINE"
        count = 0
    else:
        error_system = "OFFLINE"
        count += 1
    with open(SYSTEMUP, "w") as dataFile:
        dataFile.write("%s\n" % error_system)
        dataFile.write(str(count))


def chronos_starter(count):
    if count > 2:
        subprocess.call(["sudo", "python", CHRONOS_STARTER])
        try:
            with open(SYSTEMDOWN, "a") as dataFile:
                dataFile.write("\n%s" % datetime.datetime.today())
        except (IOError, OSError) as e:
            print "FileWriteError: %s" % e
            logging.exception("FileWriteError: %s" % e)


def led_starter():
    if not is_process_exists(LED_TRIAL):
        subprocess.call(["sudo", "python", LED_STARTER])


def wind_chill(results):
    count = 0
    windChill = 0
    for value in results:
        windChill += value[0]
        count += 1
    if count != 0:
        windChillAvg = round(windChill/count)
        with open(WIND_CHILL, "w") as dataFile:
            dataFile.write(str(windChillAvg))

if __name__ == '__main__':
    count = get_count()
    results = db_queries()
    update_systemUp(count)
    chronos_starter(count)
    led_starter()
    wind_chill(results)

import json
import serial
import time
import os
from config_parser import cfg
from pymodbus.exceptions import ModbusException
from pymodbus.client.sync import ModbusSerialClient
from db_conn import db
from flask import Flask, render_template, Response, jsonify, request, \
     make_response, flash, abort
app = Flask(__name__)

def get_data(avg=True):
    queries = ["SELECT * from mainTable order by LID desc limit 1",
               """SELECT spl.setPoint AS baselineSetPoint
                  FROM SetpointLookup AS spl
                  INNER JOIN (SELECT outsideTemp FROM mainTable ORDER BY LID DESC LIMIT 1) AS mt
                  ON spl.windChill = ROUND(mt.outsideTemp, 0)""",
               "SELECT * FROM setpoints"]
    if avg:
        queries.append("""SELECT ROUND(AVG(outsideTemp), 1) AS avgOutsideTemp
                          FROM mainTable WHERE logdatetime > DATE_SUB(CURDATE(), INTERVAL 96 HOUR)
                          ORDER BY LID DESC LIMIT 5760""")
    results = {}
    for query in queries:
            cur = db.query(query)
            results.update(cur.fetchone())
            cur.close()
    query = "SELECT * from actStream"
    cur = db.query(query)
    rows = cur.fetchall()
    cur.close()
    actStream = [{"timeStamp": row["timeStamp"].strftime("%B %d, %I:%M %p"),
                  "status": row["status"],
                  "MO": row["MO"]} for row in rows]
    return {"results": results,
            "actStream": actStream,
            "chronos_status": get_chronos_status()}

def get_chronos_status():
    chronos_status = True
    try:
        with open("/var/run/chronos.pid") as pid_file:
            pid = int(pid_file.readline())
    except IOError:
        chronos_status = False
    else:
        chronos_status = os.path.exists("/proc/{}".format(pid))
    return chronos_status

def get_modbus_data():
    boiler_stats = [0, 0, 0, 0, 0, 0]
    try:
        modbus_client = ModbusSerialClient(method=cfg.modbus.method,
                                           baudrate=cfg.modbus.baudr,
                                           parity=cfg.modbus.parity,
                                           port=cfg.modbus.portname,
                                           timeout=cfg.modbus.timeout)
        modbus_client.connect()
    except (ModbusException, OSError) as e:
        pass
    c_to_f = lambda t: round(((9.0 / 5.0) * t + 32.0), 1)
    for i in range(3):
        try:
            # Read one register from 40006 address to get System Supply Temperature
            # Memory map for the boiler is here on page 8:
            # http://www.lochinvar.com/_linefiles/SYNC-MODB%20REV%20H.pdf
            hregs = modbus_client.read_holding_registers(6, count=1, unit=1)
            # Read 9 registers from 30003 address
            iregs = modbus_client.read_input_registers(3, count=9, unit=1)
            boiler_stats = [c_to_f(hregs.getRegister(0) / 10.0),
                            c_to_f(iregs.getRegister(5) / 10.0),
                            c_to_f(iregs.getRegister(6) / 10.0),
                            c_to_f(iregs.getRegister(7) / 10.0),
                            float(iregs.getRegister(3)),
                            float(iregs.getRegister(8))]
        except (OSError, serial.SerialException, ModbusException, AttributeError, IndexError):
            time.sleep(0.7)
        else:
            break
    modbus_client.close()
    return {"system_supply_temp": boiler_stats[0],
            "outlet_temp": boiler_stats[1],
            "inlet_temp": boiler_stats[2],
            "flue_temp": boiler_stats[3],
            "cascade_current_power": boiler_stats[4],
            "lead_firing_rate": boiler_stats[5]}

@app.route("/fetch_data")
def fetch_data():
    data = get_data(avg=False)
    if "modbus" in request.args:
        data["modbus"] = get_modbus_data()
    return jsonify(data=data)

@app.route("/update_settings", methods=["POST"])
def update_settings():
    try:
        query1 = []
        if request.form["maxSetPoint"]:
            query1.append("spMax='{}'".format(request.form["maxSetPoint"]))
        if request.form["minSetPoint"]:
            query1.append("spMin='{}'".format(request.form["minSetPoint"]))
    except KeyError:
        pass
    else:
        query1 = ", ".join(query1)
        if query1:
            query1 = "UPDATE setpoints SET {}".format(query1)
            db.query(query1).close()
    query2 = []
    try:
        if request.form["cascadeTime"]:
            query2.append("CCT='{}'".format(request.form["cascadeTime"]))
    except KeyError:
        pass
    else:
        if request.form["tolerance"]:
            query2.append("t1='{}'".format(request.form["tolerance"]))
        if request.form["setPointOffset"]:
            query2.append("parameterX='{}'".format(request.form["setPointOffset"]))
        query2 = ", ".join(query2)
        if query2:
            query2 = "UPDATE mainTable SET {} ORDER BY LID DESC LIMIT 1".format(query2)
            db.query(query2).close()
    return jsonify(data=request.form)

@app.route("/switch_mode")
def switch_mode():
    mode = request.args["mode"]
    query = "UPDATE mainTable SET mode={} ORDER BY LID DESC LIMIT 1".format(int(mode))
    db.query(query).close()
    if mode in ("2", "3"):
        resp = render_template("switch_mode.html", mode=mode)
    elif mode in ("0", "1"):
        resp = make_response()
    return resp

@app.route("/")
def index():
    data = get_data()
    mode = int(data["results"]["mode"])
    if mode in (0, 2):
        data["modbus"] = get_modbus_data()
        resp = render_template("winter.html", data=data)
    elif mode in (1, 3):
        resp = render_template("summer.html", data=data)
    return resp
    
@app.route("/update_state", methods=["POST"])
def update_state():
    tid = request.form["tid"]
    status = request.form["status"]
    command = {"2": "off", "1": "on"}
    try:
        if status == "0":
            pass
        else:
            with serial.Serial(cfg.serial.portname,
                               cfg.serial.baudr,
                               timeout=1) as ser_port:
                ser_port.write("relay {} {}\n\r".format(command[status], tid))
    except (serial.SerialException, OSError) as e:
        resp = jsonify(error=True)
    else:
        query = "UPDATE actStream SET MO={} WHERE TID={}".format(status, tid)
        db.query(query).close()
        resp = make_response()
    return resp

@app.route("/winter")
def winter():
    data = get_data()
    data["modbus"] = get_modbus_data()
    return render_template("winter.html", data=data)

@app.route("/summer")
def summer():
    data = get_data()
    return render_template("summer.html", data=data)

@app.route("/chart_data")
def chart_data():
    query = "SELECT returnTemp, logdatetime, waterOutTemp from mainTable order by LID desc limit 40";
    cur = db.query(query)
    rows = cur.fetchall()
    cur.close()
    data = [{"column-1": row["waterOutTemp"],
             "column-2": row["returnTemp"],
             "date": row["logdatetime"].strftime("%Y-%m-%d %H:%M")} for row in reversed(rows)]
    resp = Response(response=json.dumps(data),
                    status=200,
                    mimetype="application/json")
    return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

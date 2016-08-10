import os
from .lib import Chronos
from .lib import db_queries
from .lib.config_parser import cfg
from flask import (Flask, render_template, Response, jsonify, request,
                   make_response)

app = Flask(__name__)
chronos = Chronos()
chronos.scheduler.start()


def get_data():
    results = {
        "outside_temp": chronos.outside_temp,
        "baseline_setpoint": chronos.baseline_setpoint,
        "tha_setpoint": chronos.tha_setpoint,
        "effective_setpoint": chronos.effective_setpoint,
        "tolerance": chronos.tolerance,
        "setpoint_min": chronos.setpoint_min,
        "setpoint_max": chronos.setpoint_max,
        "mode_change_delta_temp": chronos.mode_change_delta_temp,
        "return_temp": chronos.return_temp,
        "water_out_temp": chronos.water_out_temp,
        "mode": chronos.mode,
        "setpoint_offset_summer": chronos.setpoint_offset_summer,
        "setpoint_offset_winter": chronos.setpoint_offset_winter,
        "cascade_time": chronos.cascade_time,
        "wind_chill_avg": chronos.wind_chill_avg
    }
    efficiency = db_queries.calculate_efficiency()
    efficiency["cascade_fire_rate_avg"] = chronos.cascade_fire_rate_avg
    efficiency["hours"] = cfg.efficiency.hours
    actStream = [{
        "timeStamp": device.timestamp.strftime("%B %d, %I:%M %p"),
        "status": device.status,
        "MO": device.manual_override} for device in chronos.devices
    ]
    return {"results": results,
            "actStream": actStream,
            "chronos_status": get_chronos_status(),
            "efficiency": efficiency}


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


@app.route("/season_templates")
def get_rendered_season_templates():
    data = get_data()
    form = render_template("form.html", data=data)
    stats = render_template("stats.html", data=data)
    system_map = render_template("system_map.html", data=data)
    data = {
        "form": form,
        "stats": stats,
        "system_map": system_map
    }
    return jsonify(data)


@app.route("/download_log")
def dump_log():
    resp = Response(db_queries.log_generator(), mimetype="text/csv")
    resp.headers[
        "Content-Disposition"
    ] = "attachment; filename=exported-data.csv"
    return resp


@app.route("/update_settings", methods=["POST"])
def update_settings():
    for key, value in request.form.items():
        if value:
            setattr(chronos, key, float(value))
    return jsonify(data=request.form)


@app.route("/switch_mode", methods=["POST"])
def switch_mode():
    mode = int(request.form["mode"])
    if mode == 2:
        if not chronos.is_time_to_switch_season_to_summer:
            chronos.switch_season("to_winter")
            error = False
        else:
            error = True
    elif mode == 3:
        if not chronos.is_time_to_switch_season_to_winter:
            chronos.switch_season("to_summer")
            error = False
        else:
            error = True
    return jsonify(data=error)


@app.route("/")
def index():
    data = get_data()
    mode = int(data["results"]["mode"])
    if mode == 0:
        resp = render_template("winter.html", data=data)
    elif mode == 1:
        resp = render_template("summer.html", data=data)
    elif mode == 2:
        resp = render_template("to_winter.html", data=data)
    elif mode == 3:
        resp = render_template("to_summer.html", data=data)
    return resp


@app.route("/update_state", methods=["POST"])
def update_state():
    device_number = int(request.form["device"])
    manual_override_value = int(request.form["manual_override"])
    chronos.devices[device_number].manual_override = manual_override_value
    resp = make_response()
    return resp


@app.route("/winter")
def winter():
    data = get_data()
    return render_template("winter.html", data=data)


@app.route("/summer")
def summer():
    data = get_data()
    return render_template("summer.html", data=data)


@app.route("/chart_data")
def chart_data():
    data = db_queries.get_chart_data()
    resp = Response(response=data,
                    status=200,
                    mimetype="application/json")
    return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

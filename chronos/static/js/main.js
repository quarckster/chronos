$(document).ready(function() {
    var websocket = new ReconnectingWebSocket("ws://" + window.location.hostname + ":8000/");
    function switch_season(mode) {
        var mode = parseInt(mode);
        switch (mode) {
            case 0:
                $.get("season_templates", function(data) {
                    $("#mode-header").text("Winter mode");
                    $("#timer").text("");
                    $("#chillers-on-time").replaceWith(data.stats);
                    $("#system-map").replaceWith(data.system_map);
                    $("#form").replaceWith(data.form);
                    $(":radio").slice(0, 3).prop("disabled", false);
                    $(".pull-right > span").replaceWith(function(){
                        return $("<a class=\"switch-mode\" data-mode=\"3\" href=\"#\">" + $(this).html() + "</a>");
                    });
                    $("#winterStatus").attr("src", "static/images/Icons/WinterSummer/WOn.png");
                    $.unblockUI();
                });
                break;
            case 1:
                $.get("season_templates", function(data) {
                    $("#mode-header").text("Summer mode");
                    $("#timer").text("");
                    $("#modbus").replaceWith(data.stats);
                    $("#system-map").replaceWith(data.system_map);
                    $("#form").replaceWith(data.form); 
                    $(":radio").slice(3).prop("disabled", false);
                    $(".pull-left > span").replaceWith(function(){
                        return $("<a class=\"switch-mode\" data-mode=\"2\" href=\"#\">" + $(this).html() + "</a>");
                    });
                    $("#summerStatus").attr("src", "static/images/Icons/WinterSummer/SOn.png");
                    $.unblockUI();
                });
                break;
            case 2:
                $("#mode-header").text("Switching to winter mode in ");
                $("img[id^=\"chillerStatus\"]").attr("src", "static/images/Icons/Boiler/Chiller-OFF.png");
                $("#winterStatus").attr("src", "static/images/Icons/WinterSummer/WOff.png");
                $("#summerStatus").attr("src", "static/images/Icons/WinterSummer/SOff.png");
                $(".switch-mode").replaceWith(function(){
                        return $("<span>" + $(this).html() + "</span>");
                });
                $(":radio").prop("disabled", true);
                break;
            case 3:
                $("#mode-header").text("Switching to summer mode in ");
                $("#boilerStatus").attr("src", "static/images/Icons/Boiler/Boiler-OFF.png");
                $("#winterStatus").attr("src", "static/images/Icons/WinterSummer/WOff.png");
                $("#summerStatus").attr("src", "static/images/Icons/WinterSummer/SOff.png");
                $(".switch-mode").replaceWith(function(){
                        return $("<span>" + $(this).html() + "</span>");
                });
                $(":radio").prop("disabled", true);
        }
    }
    $(".pull-left, .pull-right").on("click", "a.switch-mode", function() {
        $.blockUI();
        var mode = $(this).data("mode");
        var post_data = {"mode": mode};
        $.post("switch_mode", post_data).done(function(data) {
            $.unblockUI();
            if (data.data.error) {
                $("#season-warning").append("<div class=\"alert center-block alert-warning alert-dismissible\" role=\"alert\"><button type=\"button\" class=\"close\" data-dismiss=\"alert\" aria-label=\"Close\"><span aria-hidden=\"true\">&times;</span></button><strong>Warning!</strong> With current parameters Chronos will automatically switch back to current season in " + data.data.mode_switch_lockout_time + " minutes</div>");
            }
        });
    });
    websocket.onmessage = function(evt) {
        var data = JSON.parse(evt.data);
        if ("device" in data) {
            switch (parseInt(data.manual_override)) {
                case 0:
                    $("#deviceAuto" + data.device).prop("checked", true);
                    break;
                case 1:
                    $("#deviceOn" + data.device).prop("checked", true);
                    break;
                case 2:
                    $("#deviceOff" + data.device).prop("checked", true);
            }
            if (parseInt(data.device) > 0) {
                switch (parseInt(data.status)) {
                    case 0:
                        $("#chillerStatus" + data.device).attr("src", "static/images/Icons/Boiler/Chiller-OFF.png");
                        break;
                    case 1:
                        $("#chillerStatus" + data.device).attr("src", "static/images/Icons/Boiler/Chiller-ON.png");
                }
                $("#chillerOnTime" + data.device).text(data.timestamp);
            } else if (parseInt(data.device) == 0) {
                switch (parseInt(data.status)) {
                    case 0:
                        $("#boilerStatus").attr("src", "static/images/Icons/Boiler/Boiler-OFF.png");
                        break;
                    case 1:
                        $("#boilerStatus").attr("src", "static/images/Icons/Boiler/Boiler-ON.png");
                }
            }
        } else if ("mode" in data) {
            switch_season(data.mode);
        } else if ("timer" in data) {
            if (parseInt(data.timer) == 0) {
                $.blockUI();
            } else {
                $("#timer").text(data.timer);
            }
        } else {
            for (var property in data) {
                if (data[property]) {
                    $("#" + property + ", ." + property).text(parseFloat(data[property]).toFixed(1));
                }
            } 
        }
    };
    $("input:radio[name$=ManualOverride]").change(function() {
        var post_data = {device: parseInt($(this)[0].id.split(/device(On|Off|Auto)/)[2]),
                         manual_override: parseInt($(this)[0].value)};
        $.blockUI();
        $.post("update_state", post_data)
               .done(function(data) {
                    if (data.error == true) {
                        $("#relay-alert").html("<div class=\"alert alert-danger\"> <a href=\"#\" class=\"close\" data-dismiss=\"alert\" aria-label=\"close\">&times;</a><strong>Error!</strong> Relay switching has been failed.</div>");
                    }
                    $.unblockUI();
              });
        });
    $("#settings").ajaxForm({
        clearForm: true,
        beforeSubmit: function(formData, jqForm, options) {
            var empty = false;
            for (var i=0; i < formData.length; i++) { 
                if (formData[i].value) { 
                    empty = true;
                }
            } 
            if (!empty) {
                alert("At least a one field should be filled.");
            }
            return empty;
        },
        success: function(responseText, statusText, xhr, $form) {
            for (var property in responseText.data) {
                if (responseText.data[property]) {
                    $("#" + property).text(parseFloat(responseText.data[property]).toFixed(1));
                }
            } 
        }
    });
});
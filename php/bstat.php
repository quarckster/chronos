<?php
function parse_bstat_output() {
	$boiler = explode(";", exec("/home/pi/Desktop/Chronos/bstat.py"));
	$boiler = array("system_supply_temp" => $boiler[0],
			   		"outlet_temp" => $boiler[1],
			   		"inlet_temp" => $boiler[2],
			   		"flue_temp" => $boiler[3],
			   		"cascade_current_power" => $boiler[4],
			   		"lead_firing_rate" => $boiler[5]);
	return $boiler;
}

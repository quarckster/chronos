<?php
function parse_bstat_output() {
    $output = array();
    exec('bstat -s /dev/ttyUSB0 2>&1', $output);
    $system_supply_temp = explode(" ", $output[0]);
    $system_supply_temp = explode("°", $system_supply_temp[7])[0];
    $outlet_temp = explode(" ", $output[1]);
    $outlet_temp = explode("°", $outlet_temp[13])[0];
    $inlet_temp = explode(" ", $output[2]);
    $inlet_temp = explode("°", $inlet_temp[14])[0];
    $flue_temp = explode(" ", $output[3]);
    $flue_temp = explode("°", $flue_temp[15])[0];
    $cascade_current_power = explode(" ", $output[4]);
    $cascade_current_power = explode("%", $cascade_current_power[5])[0];
    $lead_firing_rate = explode(" ", $output[5]);
    $lead_firing_rate = explode("%", $lead_firing_rate[11])[0];
    $data = ["system_supply_temp" => $system_supply_temp,
             "outlet_temp" => $outlet_temp,
             "inlet_temp" => $inlet_temp,
             "flue_temp" => $flue_temp,
             "cascade_current_power" => $cascade_current_power,
             "lead_firing_rate" => $lead_firing_rate];
    return $data;
}
?>
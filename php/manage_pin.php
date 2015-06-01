<?php
function manage_pin($pin, $state) {
    $output = array();
    exec('rpio -i '.$pin, $output);
    $output = explode(" ", $output[0]);
    if $output[2] != 'OUTPUT' {
        exec('rpio --setoutput='.$pin);
    }
    if ($output[3] == '(1)' and $state == 0) {
        exec('rpio -s '.$pin.':'.$state);
    } elseif ($output[3] == '(0)' and $state == 1) {
        exec('rpio -s '.$pin.':'.$state);
    }
}
?>
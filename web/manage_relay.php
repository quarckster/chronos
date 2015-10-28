<?php
include 'PhpSerial.php';

function manage_relay($relay, $command) {
    $path_to_config = "/home/pi/Desktop/Chronos/chronos_config.json";

    $json = json_decode(file_get_contents($path_to_config), true);

    $serial = new PhpSerial;

    $serial->deviceSet("/dev/ttyACM0");

    $serial->confBaudRate(19200);

    $serial->deviceOpen();

    $serial->sendMessage("relay ".$command." ".$json['relay'][$relay]."\n\r");

    $serial->deviceClose();
}
<?php
include 'PhpSerial.php';

function manage_relay($number, $command) {
    $serial = new PhpSerial;

    $serial->deviceSet("/dev/ttyACM0");

    $serial->confBaudRate(19200);

    $serial->deviceOpen();

    $serial->sendMessage("relay ".$command." ".$number."\n\r");

    $serial->deviceClose();
}
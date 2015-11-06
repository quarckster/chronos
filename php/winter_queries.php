<?php
include('SetConnect.php');
$sqls = array("SELECT outsideTemp,returnTemp,waterOutTemp,mode,setPoint2,parameterX,t1,MO_B,MO_C1,MO_C2,MO_C3,MO_C4 from mainTable order by LID desc limit 1",
              "SELECT spl.setPoint AS baselineSetPoint FROM SetpointLookup AS spl INNER JOIN (SELECT outsideTemp FROM mainTable ORDER BY LID DESC LIMIT 1) AS mt ON spl.windChill = ROUND(mt.outsideTemp, 0)",
              "SELECT status from actStream where TID=1",
              "SELECT sp FROM setpoints",
              "SELECT ROUND(AVG(outsideTemp), 2) AS avgOutsideTemp FROM mainTable WHERE logdatetime > DATE_SUB(CURDATE(), INTERVAL 96 HOUR) AND mode = 1 ORDER BY LID DESC LIMIT 5760");

$rows = array();
foreach ($sqls as $value) {
    $result = mysqli_query($con, $value);
    $rows = array_merge($rows, mysqli_fetch_array($result, MYSQLI_ASSOC));
}
$boiler = explode(";", exec("/home/pi/Desktop/Chronos/bstat.py"));
$boiler = array("system_supply_temp" => $boiler[0],
                "outlet_temp" => $boiler[1],
                "inlet_temp" => $boiler[2],
                "flue_temp" => $boiler[3],
                "cascade_current_power" => $boiler[4],
                "lead_firing_rate" => $boiler[5]);
$rows = array_merge($rows, $boiler);
echo json_encode($rows);
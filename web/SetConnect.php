<?php
$con =mysqli_connect("localhost","root","estrrado",'Chronos');
//$db_selected = mysql_select_db('Chronos', $con);
if (!$con){
  die('Could not connect: ' . mysql_error());
}
?> 
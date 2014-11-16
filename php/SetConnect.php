<?php
$con = mysql_connect("localhost","root","estrrado");
$db_selected = mysql_select_db('Chronos', $con);
if (!$con){
  die('Could not connect: ' . mysql_error());
}
?> 
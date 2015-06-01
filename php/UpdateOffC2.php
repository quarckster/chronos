<?php
header('Location:index.php');
include('SetConnect.php');
include('manage_pin.php');
// $sql="UPDATE mainTable Set MO_C2=2 ORDER BY LID DESC LIMIT 1";
$sql="UPDATE actStream SET MO=2, status=0 WHERE TID=3";
$result=mysqli_query($con,$sql);
manage_pin(16, 0);
?>
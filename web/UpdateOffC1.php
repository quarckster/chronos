<?php
header('Location:index.php');
include('SetConnect.php');
include('manage_relay.php');
$sql="UPDATE actStream SET MO=2, status=0 WHERE TID=2";
$result=mysqli_query($con,$sql);
manage_relay("chiller1", "off");
?>
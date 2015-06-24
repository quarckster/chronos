<?php
header('Location:index.php');
include('SetConnect.php');
include('manage_relay.php');
$sql="UPDATE actStream SET MO=1, status=1 WHERE TID=2";
$result=mysqli_query($con,$sql);
manage_relay(26, "on");
?>
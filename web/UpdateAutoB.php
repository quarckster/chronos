<?php
header('Location:index.php');
include('SetConnect.php');
$sql="UPDATE actStream SET MO=0 WHERE TID=1";
$result=mysqli_query($con,$sql);
?>
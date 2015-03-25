<?php
header('Location:winter.php');
include('SetConnect.php');
$sql="UPDATE mainTable Set mode=0 ORDER BY LID DESC LIMIT 1";
$result=mysqli_query($con,$sql);

?>
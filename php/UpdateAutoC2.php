<?php
header('Location:index.php');
include('SetConnect.php');
// $sql="UPDATE mainTable Set MO_C2=0 ORDER BY LID DESC LIMIT 1";
$sql="UPDATE actStream SET MO=0 WHERE TID=3";
$result=mysqli_query($con,$sql);

?>
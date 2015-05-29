<?php
header('Location:index.php');
include('SetConnect.php');
// $sql="UPDATE mainTable Set MO_C3=1 ORDER BY LID DESC LIMIT 1";
$sql="UPDATE actStream SET MO=1, status=1 WHERE TID=4";
$result=mysqli_query($con,$sql);

?>
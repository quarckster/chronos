<?php
header('Location:index.php');
include('SetConnect.php');
$sql="UPDATE mainTable Set MO_C1=0 ORDER BY LID DESC LIMIT 1";
$result=mysqli_query($con,$sql);

?>
<?php
header('Location:index.php');
include('SetConnect.php');
$sql="UPDATE mainTable Set MO_C1=1 ORDER BY LID DESC LIMIT 1";
$result=mysql_query($sql,$con);

?>
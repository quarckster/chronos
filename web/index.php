<?php
include('SetConnect.php');
$host = $_SERVER['HTTP_HOST'];
$uri = rtrim(dirname($_SERVER['PHP_SELF']), '/\\');
$sql1 = "SELECT * from mainTable order by LID desc limit 1";
$result1 = mysqli_query($con, $sql1);
if ($result1) {
    $row1 = mysqli_fetch_array($result1, MYSQLI_ASSOC);
	if ($row1['mode'] == 1) {                                                   
		header("Location: http://$host$uri/summer.php");
    } elseif ($row1['mode'] == 0) {
    	header("Location: http://$host$uri/winter.php");
    }					
}
?>
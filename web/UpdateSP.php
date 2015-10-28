<?php
header('Location:summer.php');
include('SetConnect.php');
$spMin = $_POST['spMin'];
$spMax =  $_POST['spMax'];
if($spMin != ''){
	$sql_part = "spMin='$spMin'";
}
if($spMax != ''){
	$sql_part = "spMax='$spMax'";
}
if($sql_part != ''){
	$sql = "UPDATE setpoints SET ".$sql_part;
	$result = mysqli_query($con, $sql);
}
?>

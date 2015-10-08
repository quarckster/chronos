<?php
header('Location:index.php');
include('SetConnect.php');

$parameterX = $_POST['parameterX'];
$t1 = $_POST['t1'];
$CCT = $_POST['CCT'];

$sql = "SELECT parameterX, t1, CCT from mainTable order by LID desc limit 1";
$result = mysqli_query($con,$sql);

if($result){
	$row = mysqli_fetch_array($result,MYSQLI_ASSOC);
}

if($parameterX == ''){
	$parameterX = $row['parameterX']; 
}

if($t1 == ''){
	$t1 = $row['t1'];
}

if($CCT == ''){
	$CCT = $row['CCT']; 
}

$sql="UPDATE mainTable SET parameterX='$parameterX', t1='$t1', CCT='$CCT' ORDER BY LID DESC LIMIT 1";
$result=mysqli_query($con,$sql);

?>
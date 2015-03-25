<?php
header('Location:index.php');
include('SetConnect.php');

$parameterX=$_POST['parameterX'];
$t1=$_POST['t1'];
$CCT=$_POST['CCT'];

if(($_POST['parameterX'])==''){
	$sql = "SELECT parameterX from mainTable order by LID desc limit 1";
	$result=mysqli_query($con,$sql);
	if($result){
		while($row=mysqli_fetch_array($result,MYSQLI_ASSOC)){
		$parameterX=$row['parameterX']; 
		}
	}
}
if(($_POST['t1'])==''){
	$sql = "SELECT t1 from mainTable order by LID desc limit 1";
	$result=mysqli_query($con,$sql);
	if($result){
		while($row=mysqli_fetch_array($result,MYSQLI_ASSOC)){
		$t1=$row['t1']; 
		}
	}
}
if(($_POST['CCT'])==''){
	$sql = "SELECT CCT from mainTable order by LID desc limit 1";
	$result=mysqli_query($con,$sql);
	if($result){
		while($row=mysqli_fetch_array($result,MYSQLI_ASSOC)){
		$CCT=$row['CCT']; 
		}
	}
}

$sql="UPDATE mainTable Set parameterX='$parameterX', t1='$t1', CCT='$CCT' ORDER BY LID DESC LIMIT 1";
$result=mysqli_query($con,$sql);

?>
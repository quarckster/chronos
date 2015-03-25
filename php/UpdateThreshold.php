<?php
header('Location:index.php');
include('SetConnect.php');

$parameterX=$_POST['t1'];
$parameterY=$_POST['t2'];
$parameterZ=$_POST['t3'];

if(($_POST['t1'])==''){
	$sql = "SELECT t1 from mainTable order by LID desc limit 1";
	$result=mysql_query($sql,$con);
	if($result){
		while($row=mysql_fetch_array($result)){
		$t1=$row['t1']; 
		}
	}
}
if(($_POST['t2'])==''){
	$sql = "SELECT t2 from mainTable order by LID desc limit 1";
	$result=mysql_query($sql,$con);
	if($result){
		while($row=mysql_fetch_array($result)){
		$t2=$row['t2']; 
		}
	}
}
if(($_POST['t3'])==''){
	$sql = "SELECT t3 from mainTable order by LID desc limit 1";
	$result=mysql_query($sql,$con);
	if($result){
		while($row=mysql_fetch_array($result)){
		$t3=$row['t3']; 
		}
	}
}
$sql="UPDATE mainTable Set t1='$t1', t2='$t2', t3='$t3' ORDER BY LID DESC LIMIT 1";
$result=mysql_query($sql,$con);

?>
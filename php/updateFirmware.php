<?php
header('Location:index.php');
include('SetConnect.php');
$sql="UPDATE mainTable Set powerMode=2 ORDER BY LID DESC LIMIT 1";
$result=mysqli_query($con,$sql);
sleep(8);
$targetPath = "/home/pi/Desktop/Chronos/";
$target_path =$targetPath.basename($_FILES['file']['name']);
if($_FILES['file']['name']!="")
{
	if(move_uploaded_file($_FILES['file']['tmp_name'],$target_path))
	{
		chmod($target_path,0755);
		$sql="UPDATE mainTable Set powerMode=3 ORDER BY LID DESC LIMIT 1";
		$result=mysqli_query($con,$sql);
	
	}
	else
	{
		$sql="UPDATE mainTable Set powerMode=4 ORDER BY LID DESC LIMIT 1";
		$result=mysqli_query($con,$sql);
		
	}
		
}
else
{
	echo "File Not specified";
	
}

?>
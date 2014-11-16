<?php
header('Content-Type: image/png');
$myFileTin =fopen("sysStatus.txt","r") or die("Unable to open File");
$members = array();
while(!feof($myFileTin)){
	$members[]=fgets($myFileTin);
	
}
	if($members[0]== 0 && $members[1]==0)
		readfile('images/Icons/TINTOUT/TOTO.png');
	else if($members[0]== 1 && $members[1]==1)
		readfile('images/Icons/TINTOUT/TFTF.png');
	else if($members[0]== 1 && $members[1]==0)
		readfile('images/Icons/TINTOUT/TFTO.png');
	else if($members[0]== 0 && $members[1]==1)
		readfile('images/Icons/TINTOUT/TOTF.png');

fclose($myFileTin);
?>
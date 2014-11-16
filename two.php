<?php
	$myFileTin =fopen("sysStatus.txt","r") or die("Unable to open File");
	$members = array();
	while(!feof($myFileTin)){
		$members[]=fgets($myFileTin);
		
	}
		if($members[2]== 0 && $members[3]==0)
			readfile('images/Icons/DBWEB/DODBO.png');
		else if($members[2]== 1 && $members[3]==1)
			readfile('images/Icons/DBWEB/DFDBF.png');
		else if($members[2]== 1 && $members[3]==0)
			readfile('images/Icons/DBWEB/DFDBO.png');
		else if($members[2]== 0 && $members[3]==1)
			readfile('images/Icons/DBWEB/DODBF.png');
	
	fclose($myFileTin);
?>
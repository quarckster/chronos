<?php
	$myFileTin =fopen("sysStatus.txt","r") or die("Unable to open File");
	$members = array();
	while(!feof($myFileTin)){
		$members[]=fgets($myFileTin);
		
	}
		if($members[4]== 0)
			readfile('images/Icons/GPIO/GPIOO.png');
		else if($members[4]== 1)
			readfile('images/Icons/GPIO/GPIOF.png');
		

	fclose($myFileTin);
?>

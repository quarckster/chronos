<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <!--<meta http-equiv="refresh" content=5>-->
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" type="image/png" href="images/Icons/Logo.png">
    <title>Chronos : Home Page</title>
	
    <!-- Bootstrap -->
  	<script src="amcharts/amcharts.js" type="text/javascript"></script>
	<script src="amcharts/serial.js" type="text/javascript"></script>	
	<script src="http://code.jquery.com/jquery-latest.js" type="text/javascript"></script>
	<script type="text/javascript">
		setInterval("my_function();",1700);
		function my_function()
		{
			$("#updateSetpoint").load("index.php #inside");
		}
		setInterval("my_functionImage();",1800);
		function my_functionImage()
		{
			$("#updateImage").load("index.php #insideImage");
		}
		setInterval("my_functionInterface();",1900);
		function my_functionInterface()
		{
			$("#updateInterface").load("index.php #insideInterface");
		}
		setInterval("my_functionSetpoint();",2500);
		function my_functionSetpoint()
		{
			$("#updateSetpointtwo").load("index.php #insidetwo");
		}
		setInterval("my_functionSetpointTwo();",6100);
		function my_functionSetpointTwo()
		{
			$("#updateSetpointThree").load("index.php #insideThree");
		}
    $(function () { 
    $("[data-toggle='tooltip']").tooltip(); 
    });
	</script>	

	<!-- amCharts javascript code -->
		<script type="text/javascript">
          <?php
						include('SetConnect.php');
						$sql="SELECT returnTemp from mainTable order by LID desc limit 20";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							$arr[] = $row['returnTemp']; 
							}
						}
					?>;
     <?php
						include('SetConnect.php');
						$sql="SELECT logdatetime from mainTable order by LID desc limit 20";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							$arrDate[] = $row['logdatetime']; 
							}
						}
               
					?>;

    
		var d = new Date();
		var n = d.getMinutes();
		AmCharts.makeChart("chartdiv",
				{
					"type": "serial",
					"pathToImages": "http://cdn.amcharts.com/lib/3/images/",
					"categoryField": "date",
					"dataDateFormat": "YYYY-MM-DD HH:NN",
					"categoryAxis": {
						"minPeriod": "mm",
						"parseDates": true
					},
					"chartCursor": {
						"categoryBalloonDateFormat": "JJ:NN"
					},
					"chartScrollbar": {},
					"trendLines": [],
					"graphs": [
						{
							"bullet": "round",
							"id": "AmGraph-1",
							"title": "graph 1",
							"valueField": "column-1"
						}
					],
					"guides": [],
					"valueAxes": [
						{
							"id": "ValueAxis-1",
							"title": "Temperature"
						}
					],
					"allLabels": [],
					"balloon": {},
					
					"titles": [
						{
							"id": "Title-1",
							"size": 14,
							"text": "Chart - Water Inlet"
						}
					],
            "dataProvider": [
            {
							"column-1": <?php echo $arr[19];?>,
							"date": "<?php echo substr($arrDate[19],0,16);?>"
						},
						{
							"column-1": <?php echo $arr[18];?>,
							"date": "<?php echo substr($arrDate[18],0,16);?>"
						},
						{
							"column-1": <?php echo $arr[17];?>,
							"date": "<?php echo substr($arrDate[17],0,16);?>"
						},
						{
							"column-1": <?php echo $arr[16];?>,
							"date": "<?php echo substr($arrDate[16],0,16);?>"
						},
						{
							"column-1": <?php echo $arr[15];?>,
							"date": "<?php echo substr($arrDate[15],0,16);?>"
						},
						{
							"column-1": <?php echo $arr[14];?>,
							"date": "<?php echo substr($arrDate[14],0,16);?>"
						},
						{
							"column-1": <?php echo $arr[13];?>,
							"date": "<?php echo substr($arrDate[13],0,16);?>"
						},
						{
							"column-1": <?php echo $arr[12];?>,
							"date": "<?php echo substr($arrDate[12],0,16);?>"
						},
						{
							"column-1": <?php echo $arr[11];?>,
							"date": "<?php echo substr($arrDate[11],0,16);?>"
						},
						{
							"column-1": <?php echo $arr[10];?>,
							"date": "<?php echo substr($arrDate[10],0,16);?>"
						},
						{
							"column-1": <?php echo $arr[9];?>,
							"date": "<?php echo substr($arrDate[9],0,16);?>"
						},
						{
							"column-1": <?php echo $arr[8];?>,
							"date": "<?php echo substr($arrDate[8],0,16);?>"
						},
						{
							"column-1": <?php echo $arr[7];?>,
							"date": "<?php echo substr($arrDate[7],0,16);?>"
						},
            {
							"column-1": <?php echo $arr[6];?>,
							"date": "<?php echo substr($arrDate[6],0,16);?>"
						},
						{
							"column-1": <?php echo $arr[5];?>,
							"date": "<?php echo substr($arrDate[5],0,16);?>"
						},
						{
							"column-1": <?php echo $arr[4];?>,
							"date": "<?php echo substr($arrDate[4],0,16);?>"
						},
						{
							"column-1": <?php echo $arr[3];?>,
							"date": "<?php echo substr($arrDate[3],0,16);?>"
						},
						{
							"column-1": <?php echo $arr[2];?>,
							"date": "<?php echo substr($arrDate[2],0,16);?>"
						},
						{
							"column-1": <?php echo $arr[1];?>,
							"date": "<?php echo substr($arrDate[1],0,16);?>"
						},
						{
							"column-1": <?php echo $arr[0];?>,
							"date": "<?php echo substr($arrDate[0],0,16);?>"
						}
   
					]
				}
			);
		</script>

		<script type="text/javascript">
          <?php
						include('SetConnect.php');
						$sql="SELECT waterOutTemp from mainTable order by LID desc limit 20";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							$arr1[] = $row['waterOutTemp']; 
							}
						}
					?>;
     <?php
						include('SetConnect.php');
						$sql="SELECT logdatetime from mainTable order by LID desc limit 20";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							$arrDate1[] = $row['logdatetime']; 
							}
						}
               
					?>;

    
		var d1 = new Date();
		var n1 = d1.getMinutes();
		AmCharts.makeChart("chartdiv1",
				{
					"type": "serial",
					"pathToImages": "http://cdn.amcharts.com/lib/3/images/",
					"categoryField": "date",
					"dataDateFormat": "YYYY-MM-DD HH:NN",
					"categoryAxis": {
						"minPeriod": "mm",
						"parseDates": true
					},
					"chartCursor": {
						"categoryBalloonDateFormat": "JJ:NN"
					},
					"chartScrollbar": {},
					"trendLines": [],
					"graphs": [
						{
							"bullet": "round",
							"id": "AmGraph-1",
							"title": "graph 1",
							"valueField": "column-1"
						}
					],
					"guides": [],
					"valueAxes": [
						{
							"id": "ValueAxis-1",
							"title": "Temperature"
						}
					],
					"allLabels": [],
					"balloon": {},
					
					"titles": [
						{
							"id": "Title-1",
							"size": 14,
							"text": "Chart - Water Outlet"
						}
					],
            "dataProvider": [
            {
							"column-1": <?php echo $arr1[19];?>,
							"date": "<?php echo substr($arrDate1[19],0,16);?>"
						},
						{
							"column-1": <?php echo $arr1[18];?>,
							"date": "<?php echo substr($arrDate1[18],0,16);?>"
						},
						{
							"column-1": <?php echo $arr1[17];?>,
							"date": "<?php echo substr($arrDate1[17],0,16);?>"
						},
						{
							"column-1": <?php echo $arr1[16];?>,
							"date": "<?php echo substr($arrDate1[16],0,16);?>"
						},
						{
							"column-1": <?php echo $arr1[15];?>,
							"date": "<?php echo substr($arrDate1[15],0,16);?>"
						},
						{
							"column-1": <?php echo $arr1[14];?>,
							"date": "<?php echo substr($arrDate1[14],0,16);?>"
						},
						{
							"column-1": <?php echo $arr1[13];?>,
							"date": "<?php echo substr($arrDate1[13],0,16);?>"
						},
						{
							"column-1": <?php echo $arr1[12];?>,
							"date": "<?php echo substr($arrDate1[12],0,16);?>"
						},
						{
							"column-1": <?php echo $arr1[11];?>,
							"date": "<?php echo substr($arrDate1[11],0,16);?>"
						},
						{
							"column-1": <?php echo $arr1[10];?>,
							"date": "<?php echo substr($arrDate1[10],0,16);?>"
						},
						{
							"column-1": <?php echo $arr1[9];?>,
							"date": "<?php echo substr($arrDate1[9],0,16);?>"
						},
						{
							"column-1": <?php echo $arr1[8];?>,
							"date": "<?php echo substr($arrDate1[8],0,16);?>"
						},
						{
							"column-1": <?php echo $arr1[7];?>,
							"date": "<?php echo substr($arrDate1[7],0,16);?>"
						},
            {
							"column-1": <?php echo $arr1[6];?>,
							"date": "<?php echo substr($arrDate1[6],0,16);?>"
						},
						{
							"column-1": <?php echo $arr1[5];?>,
							"date": "<?php echo substr($arrDate1[5],0,16);?>"
						},
						{
							"column-1": <?php echo $arr1[4];?>,
							"date": "<?php echo substr($arrDate1[4],0,16);?>"
						},
						{
							"column-1": <?php echo $arr1[3];?>,
							"date": "<?php echo substr($arrDate1[3],0,16);?>"
						},
						{
							"column-1": <?php echo $arr1[2];?>,
							"date": "<?php echo substr($arrDate1[2],0,16);?>"
						},
						{
							"column-1": <?php echo $arr1[1];?>,
							"date": "<?php echo substr($arrDate1[1],0,16);?>"
						},
						{
							"column-1": <?php echo $arr1[0];?>,
							"date": "<?php echo substr($arrDate1[0],0,16);?>"
						}
   
					]
				}
			);
		</script>
 
	<!--Water Outlet-->

	<script type="text/javascript">
		
	</script>




	<link href="css/style.css" rel="stylesheet">
	<link href="css/bootstrap.min.css" rel="stylesheet">
	<link href="css/graph.css" rel="stylesheet">
	<style>
		#canvas .circle {
			display: inline-block;
			margin: 1em;
		}

		.circles-decimals {
			font-size: .4em;
		}
		    .btn-file {
    
    height:30px;
    position: relative;
    overflow: hidden;
    }
    .btn-file input[type=file] {
    position: absolute;
    top: 0;
    right: 0;
    min-width: 100%;
    min-height: 100%;
    text-align: right;
    filter: alpha(opacity=0);
    opacity: 0;
    outline: none;
    background: white;
    cursor: inherit;
    display: block;
    }

	
	</style>
    <!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
  </head>
  <body style="font-family:segoe ui;">
  <script type="text/javascript">
<!--
    function toggle_visibility(id) {
       var e = document.getElementById(id);
       if(e.style.display == 'block')
          e.style.display = 'none';
       else
          e.style.display = 'block';
    }
//-->
</script>
	<!-- Top Container -->
	
	<div class="container-fluid" style="background-color:#3D7073;">
		<div id = "updateSetpointThree" class="container jumbotron" style="background-color:#3D7073; padding-top:0; padding-bottom:2px; margin-bottom:0; ">
			<div id = "insideThree" class="row" >
				<div class="col-md-3" style="text-align:center; color:#FFFFFF; background-color:#1E3839; padding:10px 10px;">
					<h4><b>CHRONOS</b></h4>
					<h5>SYSTEM - <?php
					$myFileSys =fopen("/var/www/systemUp.txt","r") or die("Unable to open File");
					$members = array();
					while(!feof($myFileSys)){
						$members[]=fgets($myFileSys);
						
					}
						echo $members[0];
				
					fclose($myFileTin);
				?></h5><!--Dynamic Content-->
				</div>
				<div class="col-md-6" style="text-align:center; color:#FFFFFF;">
					<h6><a href="#" style="color:#FFFFFF;">About</a> | 
					<a href="#" style="color:#FFFFFF;">Developer Website</a> |
					<a href="#" style="color:#FFFFFF;">Help</a></h6>
					
						<div class="col-md-12"  style="background-color:#1E3839; min-height:50px; padding-top:5px; padding-bottom:5px;">
							<h5>SYSTEM MAP</h5>
						</div>
					
				</div>
				<div class="hidden-xs">
				<div class="col-md-3" style="text-align:center; color:#FFFFFF; text-align:center; color:#FFFFFF; background-color:#1E3839; min-height:84px;">
				<br/>
					<div style="min-width:60px; font-size:10px; color:#FFFFFF; float:left; text-align=center;">
						&nbsp;
						</div>
						<div style="min-width:80px; font-size:10px; color:#FFFFFF; float:left; text-align=center;">
						<img src="<?php
						include('SetConnect.php');
						$sql="SELECT mode from mainTable order by LID desc limit 1";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							if($row['mode']==0)
								echo "images/Icons/WinterSummer/WOn.png";
							else if($row['mode']==1)
								echo "images/Icons/WinterSummer/WOff.png";
							
							}
						}
					?>" /><br/><a href="updateModeOn.php" font-size:10px;">Winter</a>
						</div>
					
					<div style=" min-width:80px; font-size:10px; color:#FFFFFF; float:left; text-align=center;">
						<img src="<?php
						include('SetConnect.php');
						$sql="SELECT mode from mainTable order by LID desc limit 1";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							if($row['mode']==0)
								echo "images/Icons/WinterSummer/SOff.png";
							else if($row['mode']==1)
								echo "images/Icons/WinterSummer/SOn.png";
							
							}
						}
					?>" /><br/><a href="updateModeOff.php" style="color:#FFFFFF; font-size:10px;">Summer</a>
					</div>

					
				</div>
				</div>
			</div>
		</div>
	</div>
	<!-- End of Top Container -->
	
	<div class="container-fluid" style="background-color:#3D7073;">
		<div class="container jumbotron" style="background-color:#3D7073; padding-bottom:0; padding-top:2px;">
			<div class="row">
			     <div id="updateSetpoint">
				<div class="col-md-3" id="inside" style="text-align:center; color:#FFFFFF; background-color:#224042; padding:0 0; min-height:360px;">
					<div style="width:100%; background-color:#FF6600; padding:10px 10px;" >
					<b>System Statistics</b>
					</div>
					<br/>
					<h5 style="font-size:15px;"><?php
						include('SetConnect.php');
						$sql="SELECT mode FROM mainTable ORDER BY LID DESC LIMIT 1";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							if ($row[mode]==0)
								echo "Wind Chill"; 
							else if ($row[mode]==1)
								echo "Outside Temperature";
							}
						}
					?></h5>
					<h6 id="OutsideTemp"><?php
						include('SetConnect.php');
						$sql="SELECT outsideTemp from mainTable order by LID desc limit 1";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							echo $row['outsideTemp']; 
							}
						}
					?> &deg;F</h6>		<!--Dynamic Content-->
					<h6><small style="color:#FFFFFF;"><a href="http://wx.thomaslivestock.com" style="color:#FFFFFF;">wx.thomaslivestock.com</a></small></h6>
					<div style="height:15px;"></div>
					<table  align=center>
						<tr>
						<td >Water Inlet</td>
						<td width=5% style="border-right:1px solid rgba(255, 255, 255, 0.5);"></td>
						<td>&nbsp;&nbsp;&nbsp;Water Outlet</td><!--Dynamic Content-->
						</tr>
						<tr>
						<td><?php
						include('SetConnect.php');
						$sql="SELECT returnTemp from mainTable order by LID desc limit 1";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							echo $row['returnTemp']; 
							}
						}
					?> &deg;F</td>
						<td width=5% style="border-right:1px solid rgba(255, 255, 255, 0.5);"></td>
						<td><?php
						include('SetConnect.php');
						$sql="SELECT waterOutTemp from mainTable order by LID desc limit 1";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							echo $row['waterOutTemp']; 
							}
						}
					?> &deg;F</td><!--Dynamic Content-->
						</tr>
						
					</table>
					<hr/ style="opacity:0.5;">
					<table align=center style="font-size:13px;">
                 <br/>
						<h6 style="font-size:14px;">Activity Stream</h6>
						<tr>
						<td></td>
						<td width=5% style="border-left:1px solid rgba(255, 255, 255, 0.5);"></td>
						<td>&nbsp;&nbsp;&nbsp;Date &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Time</td><!--Dynamic Content-->
						<td width=5% style="border-right:1px solid rgba(255, 255, 255, 0.5);"></td>
						<td>&nbsp;&nbsp;&nbsp;Status</td>
						</tr>
						<tr>
						<td>Boiler&nbsp;&nbsp;</td>
						<td width=5% style="border-left:1px solid rgba(255, 255, 255, 0.5);"></td>
						<td><?php
						include('SetConnect.php');
						$sql="SELECT timeStamp from actStream where TID=1";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							echo $row['timeStamp']; 
							}
						}
					?></td><!--Dynamic Content-->
						<td width=5% style="border-right:1px solid rgba(255, 255, 255, 0.5);"></td>
						<td><?php
						include('SetConnect.php');
						$sql="SELECT status from actStream where TID=1";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							if ($row[status]==1)
								echo "ON"; 
							else if ($row[status]==0)
								echo "OFF";
							}
						}
					?></td>
						</tr>
						<tr>
						<td>Chiller 1&nbsp;&nbsp;</td>
						<td width=5% style="border-left:1px solid rgba(255, 255, 255, 0.5);"></td>
						<td><?php
						include('SetConnect.php');
						$sql="SELECT timeStamp from actStream where TID=2";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							echo $row['timeStamp']; 
							}
						}
					?></td><!--Dynamic Content-->
						<td width=5% style="border-right:1px solid rgba(255, 255, 255, 0.5);"></td>
						<td><?php
						include('SetConnect.php');
						$sql="SELECT status from actStream where TID=2";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							if ($row[status]==1)
								echo "ON"; 
							else if ($row[status]==0)
								echo "OFF";
							}
						}
					?></td>
						</tr>
						<tr>
						<td>Chiller 2&nbsp;&nbsp;</td>
						<td width=5% style="border-left:1px solid rgba(255, 255, 255, 0.5);"></td>
						<td><?php
						include('SetConnect.php');
						$sql="SELECT timeStamp from actStream where TID=3";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							echo $row['timeStamp']; 
							}
						}
					?></td><!--Dynamic Content-->
						<td width=5% style="border-right:1px solid rgba(255, 255, 255, 0.5);"></td>
						<td><?php
						include('SetConnect.php');
						$sql="SELECT status from actStream where TID=3";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							if ($row[status]==1)
								echo "ON"; 
							else if ($row[status]==0)
								echo "OFF";
							}
						}
					?></td>
						</tr>
					</table>
					<br/>
					<br/>
               
				</div>
			    </div>
				<div id=Just data-toggle="tooltip" data-placement="down" data-original-title="<?php
						include('SetConnect.php');
						$sql="SELECT mode from mainTable order by LID desc limit 1";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							if($row['mode']==0)
								echo "Effective Setpoint = Dynamic Setpoint + Boiler Offset";
							else if($row['mode']==1)
								echo "Effective Setpoint = Dynamic Setpoint + Chiller1 Offset";
							
							}
						}
					?>" style="position:absolute; z-index:100; right:180px; top:270px; min-height:40px; min-width:60px;">
            
        </div>
				<div class="col-md-6" id="updateImage" style="text-align:center; color:#FFFFFF; min-height:300px;">
					<div  id="insideImage" style="width:100%; margin-top:30px; padding:10px 10px; background-image:url('<?php
						include('SetConnect.php');
						$sql="SELECT returnTemp from mainTable order by logdatetime desc limit 1";
						$sql2="SELECT waterOutTemp from mainTable order by LID desc limit 1";
						$result=mysql_query($sql,$con);
						$result1=mysql_query($sql2,$con);
						if($result){
							while(($row=mysql_fetch_array($result)) && ($row1=mysql_fetch_array($result1))){
							if ($row[returnTemp]>=80&&$row1[waterOutTemp]>=80)
								echo "images/Icons/MainImage/OHIH.png"; 
							else if ($row[returnTemp]<80&&$row1[waterOutTemp]<80)
								echo "images/Icons/MainImage/OCIC.png"; 
							else if ($row[returnTemp]<80&&$row1[waterOutTemp]>=80)
								echo "images/Icons/MainImage/OHIC.png"; 
							else if ($row[returnTemp]>=80&&$row1[waterOutTemp]<80)
								echo "images/Icons/MainImage/OCIH.png";
							}
						}
					?>'); font-size:11px; background-repeat: no-repeat; min-height:300px;" >
						<table border="0" >
							<tr height=30px>
								<td width="55%"></td>
								<td></td>
								<td></td>
								<td></td>
								<td></td>
							<tr>
							<tr>
								<td ></td>
								<td width=11%></td>	
								<td></td>
								<td></td>
								<td align="right"></td>
							<tr>
							<tr>
								<td></td>
								<td></td>
								<td align="left"><div><br/><img src="<?php
						include('SetConnect.php');
						$sql="SELECT status from actStream where TID=1";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							if ($row[status]==1)
								echo "images/Icons/Boiler/Boiler-ON.png"; 
							else if ($row[status]==0)
								echo "images/Icons/Boiler/Boiler-OFF.png"; 
							
							}
						}
					?>" /></div></td>
								<td></td>
								<td></td>
							<tr>
							<tr>
								<td></td>
								<td></td>	
								<td align="left">&nbsp;Boiler 1</td>
								<td></td>
								<td></td>
							<tr>
							<tr>
								<td></td>
								<td></td>
								<td align="left" width=100px><br/><img src="<?php
						include('SetConnect.php');
						$sql="SELECT status from actStream where TID=2";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							if ($row[status]==1)
								echo "images/Icons/Boiler/Chiller-ON.png"; 
							else if ($row[status]==0)
								echo "images/Icons/Boiler/Chiller-OFF.png"; 
							
							}
						}
					?>" /></td>
								<td align="left"><br/><img src="<?php
						include('SetConnect.php');
						$sql="SELECT status from actStream where TID=3";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							if ($row[status]==1)
								echo "images/Icons/Boiler/Chiller-ON.png"; 
							else if ($row[status]==0)
								echo "images/Icons/Boiler/Chiller-OFF.png"; 
							
							}
						}
					?>"/></td>
								<td></td>
							<tr>
							<tr>
								<td></td>
								<td></td>
								<td align="left">Chiller 1</td>
								<td align="left">Chiller 2</td>
								<td></td>
							<tr>
						</table>
					</div>
					
				</div>
			
				<div class="col-md-3" style="text-align:center; color:#FFFFFF; background-color:#224042; padding:0 0; min-height:360px;">
			
			

					<div style="width:100%; background-color:#FF6600; padding:10px 10px;" >
					<b>User Settings</b>
					</div>
				<br/>
				<div id="updateSetpointtwo">
				<div  id="insidetwo" style="text-align:center; color:#FFFFFF; background-color:#224042; padding:0 0;">
					
					<h5 style="font-size:15px;">Dynamic Setpoint</h5>
					<h6 id="OutsideTemp"><?php
						include('SetConnect.php');
						$sql="SELECT setPoint2 from mainTable order by LID desc limit 1";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							echo $row['setPoint2']; 
							}
						}
					?> &deg;F</h6>		<!--Dynamic Content-->
					<h6 ><small style="color:#FFFFFF;">Average <?php
						include('SetConnect.php');
						$sql="SELECT mode FROM mainTable ORDER BY LID DESC LIMIT 1";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							if ($row[mode]==0)
								echo "Wind Chill"; 
							else if ($row[mode]==1)
								echo "Outside Temperature";
							}
						}
					?> (24 Hours) = <?php
					$myFileWC =fopen("/home/pi/Desktop/Chronos/windChillAvg.txt","r") or die("Unable to open File");
					$members = array();
					while(!feof($myFileWC)){
						$members[]=fgets($myFileWC);
						
					}
						echo $members[0];
				
					fclose($myFileTin);
				?> </small></h6>
					<div style="height:5px;"></div>			
					<h5 style="font-size:15px;">Effective Setpoint</h5>
					<h6 id="OutsideTemp"><?php
						include('SetConnect.php');
						$sql="SELECT mode from mainTable order by LID desc limit 1";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							$a = $row['mode']; 
							}
						}
						$sql="SELECT setPoint2 from mainTable order by LID desc limit 1";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							$b = $row['setPoint2']; 
							}
						}
						$sql="SELECT parameterY from mainTable order by LID desc limit 1";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							$c = $row['parameterY']; 
							}
						}
            $sql="SELECT parameterX from mainTable order by LID desc limit 1";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							$d = $row['parameterX']; 
							}
						}
						if($a){
							echo ($b + $c);
						}
						else{
							echo ($b + $d);
						}
					?> &deg;F</h6>		<!--Dynamic Content-->
				</div>
			    </div>
					
          <hr/ style="opacity:0.5;">
<div class="flip-container" id = "flip-toggle" ontouchstart="this.classList.toggle('hover');">
	<div class="flipper">
       <form name="UpdateParameter" action="UpdatePara.php" method=post>

	    <div class="front">
         
			  <h6 style="font-size:14px;">Offset Parameters</h6>
					
					<table border=0 align=center>
						
						<tr>
						<td>Boiler</td>
						<td width=5%></td>
						<td><?php
						include('SetConnect.php');
						$sql="SELECT parameterX from mainTable order by LID desc limit 1";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							echo $row['parameterX']; 
							}
						}
					?> &deg;F</td><td ></td>
						<td style="color:#000000;"><input type="text" name="parameterX" size=2></td><!--Dynamic Content-->
						<td width=3%></td>
						<td><input type="Submit" value="Update" style="color:#000000;"></td>
						</tr>
            <tr>
						<td>Chiller 1</td>
						<td width=5%></td>
						<td><?php
						include('SetConnect.php');
						$sql="SELECT parameterY from mainTable order by LID desc limit 1";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							echo $row['parameterY']; 
							}
						}
					?> &deg;F</td><td ></td>
						<td style="color:#000000;"><input type="text" name="parameterY" size=2></td><!--Dynamic Content-->
						<td width=3%></td>
						<td><input type="Submit" value="Update" style="color:#000000;"></td>
						</tr>
						<tr>
						<td>Chiller 2</td>
						<td width=5%></td>
						<td><?php
						include('SetConnect.php');
						$sql="SELECT parameterZ from mainTable order by LID desc limit 1";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							echo $row['parameterZ']; 
							}
						}
					?> &deg;F</td><!--Dynamic Content--><td >&nbsp;&nbsp;</td>
						<td style="color:#000000;"><input type="text" name="parameterZ" size=2></td>
						<td width=3%></td>
						<td><input type="Submit" value="Update" style="color:#000000;"></td>
						</tr>
					</table>
		</div>
   
   
		<div class="back">
			<!-- back content -->
      
			  <h6 style="font-size:14px;">Tolerance Parameters</h6>
					
      <table border=0 align=center>
					
						<tr>
						<td>Boiler (t1)</td>
						<td width=5%></td>
						<td><?php
						include('SetConnect.php');
						$sql="SELECT t1 from mainTable order by LID desc limit 1";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							echo $row['t1']; 
							}
						}
					?> &deg;F</td><td ></td>
						<td style="color:#000000;"><input type="text" name="t1" size=2></td><!--Dynamic Content-->
						<td width=3%></td>
						<td><input type="Submit" value="Update" style="color:#000000;"></td>
						</tr>
            <tr>
						<td>Chiller 1 (t2)</td>
						<td width=5%></td>
						<td><?php
						include('SetConnect.php');
						$sql="SELECT t2 from mainTable order by LID desc limit 1";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							echo $row['t2']; 
							}
						}
					?> &deg;F</td><td ></td>
						<td style="color:#000000;"><input type="text" name="t2" size=2></td><!--Dynamic Content-->
						<td width=3%></td>
						<td><input type="Submit" value="Update" style="color:#000000;"></td>
						</tr>
						<tr>
						<td>Chiller 2 (t3)</td>
						<td width=5%></td>
						<td><?php
						include('SetConnect.php');
						$sql="SELECT t3 from mainTable order by LID desc limit 1";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							echo $row['t3']; 
							}
						}
					?> &deg;F</td><!--Dynamic Content--><td >&nbsp;&nbsp;</td>
						<td style="color:#000000;"><input type="text" name="t3" size=2></td>
						<td width=3%></td>
						<td><input type="Submit" value="Update" style="color:#000000;"></td>
						</tr>
					</table>
		</div>
    </form>
	</div>
</div> 

<button onclick="document.querySelector('#flip-toggle').classList.toggle('hover');" class="toggleButton">Toggle</button>		
				</div>
			</div>
		</div>
	</div>
	
	
	<div class="container-fluid" style="background-color:#3D7073;">
		<div class="container jumbotron" style="background-color:#3D7073; margin-bottom:0; padding-bottom:0; padding-top:5px;">
			<div class="row" >
				<div class="col-md-3" style="text-align:center; color:#FFFFFF; background-color:#1E3839;">
					<div style="width:100%; background-color:#1E3839; padding:20px 20px;" >
					
					</div>
				</div>
				<div class="col-md-6" style="text-align:center; color:#FFFFFF;">
				
					<div style="width:100%; background-color:#1E3839; padding:8px 8px;" >
						<span class="button"><a href="updateReboot.php"  style="color:#000000; font-size:12px">System Reboot</a></span>
					</div>
					
				</div>
				<div class="hidden-xs">
				<div class="col-md-3" style="text-align:center; color:#FFFFFF; text-align:center; color:#FFFFFF; background-color:#1E3839;  padding:0 0;">
					
					<div style="width:100%; background-color:#1E3839; padding:20px 20px;" >
					
					</div>
					<!--<div style="width:100%; background-color:#FF6600; padding:10px 10px;" >
					<b>ModBus Communication</b>
					</div>
					
					<h5></h5>
					<h6 id="OutsideTemp">OFFLINE</h6>	-->	<!--Dynamic Content-->
					
				</div>
				</div>
			</div>
		</div>
	</div>
	
	<div class="container-fluid" id="updateInterface" style="background-color:#FFFFFF;">
		<div class="container jumbotron" id="insideInterface" style="background-color:#FFFFFF; margin-bottom:0; padding-bottom:0; padding-top:5px;">
			<div class="row" >
				<div class="col-md-4" style="width: 150px; text-align:center; color:#3D7073;">
				</div>
				<div class="col-md-4" style="text-align:center; color:#3D7073; ">
					<h5>MANUAL OVERRIDE</h5><br/>
					<div style="min-height:100px; min-width:35px; float:left;">
							
						</div>
						<div style="background-image:url('<?php
						include('SetConnect.php');
						$sql="SELECT MO_B from mainTable order by LID desc limit 1";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							if($row['MO_B']==0)
								echo "images/Icons/Manual/Auto.png";
							else if($row['MO_B']==1)
								echo "images/Icons/Manual/ON.png";
							else if($row['MO_B']==2)
								echo "images/Icons/Manual/OFF.png";
							}
						}
					?>'); 	background-repeat: no-repeat; min-height:100px; min-width:110px; font-size:10px; color:#FFFFFF; float:left;">
							<table border=0>
								<tr height=10%>
								<td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
								<td></td>
								<td></td>
								<td></td>
								<td></td>
								<td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
								</tr>
								<tr>
								<tr height=15px>
								<td></td>
								<td></td>
								<td></td>
								<td></td>
								<td></td>
								<td></td>
								</tr>
								<tr>
								<td></td>
								<td></td>
								<td><a href="UpdateAutoB.php">&nbsp;Auto</a></td>
								<td></td>
								<td><a href="UpdateOnB.php">On</a></td>
								<td></td>
								</tr>
								<tr >
								<td>&nbsp;</td>
								<td></td>
								<td></td>
								<td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
								<td></td>
								<td></td>
								</tr>
								<tr>
								<td></td>
								<td></td>
								<td></td>
								<td><a href="UpdateOffB.php">Off</a></td>
								<td></td>
								<td></td>
								</tr>
								<tr height=5%>
								<td colspan=6>&nbsp;</td>
								</tr>
								<tr height=5%>
								<td colspan=6>&nbsp;</td>
								</tr>
								<tr>
								<td colspan=6 style="color:#3D7073; font-size:12px;">&nbsp;&nbsp;&nbsp;Boiler</td>
								</tr>

							</table>
							
							
						</div>
						<div style="background-image:url('<?php
						include('SetConnect.php');
						$sql="SELECT MO_C1 from mainTable order by LID desc limit 1";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							if($row['MO_C1']==0)
								echo "images/Icons/Manual/Auto.png";
							else if($row['MO_C1']==1)
								echo "images/Icons/Manual/ON.png";
							else if($row['MO_C1']==2)
								echo "images/Icons/Manual/OFF.png";
							}
						}
					?>'); 	background-repeat: no-repeat; min-height:100px; min-width:110px; font-size:10px; color:#FFFFFF; float:left;">
							<table border=0>
								<tr height=10%>
								<td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
								<td></td>
								<td></td>
								<td></td>
								<td></td>
								<td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
								</tr>
								<tr>
								<tr height=15px>
								<td></td>
								<td></td>
								<td></td>
								<td></td>
								<td></td>
								<td></td>
								</tr>
								<tr>
								<td></td>
								<td></td>
								<td><a href="UpdateAutoC1.php">&nbsp;Auto</a></td>
								<td></td>
								<td><a href="UpdateOnC1.php">On</a></td>
								<td></td>
								</tr>
								<tr >
								<td>&nbsp;</td>
								<td></td>
								<td></td>
								<td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
								<td></td>
								<td></td>
								</tr>
								<tr>
								<td></td>
								<td></td>
								<td></td>
								<td><a href="UpdateOffC1.php">Off</a></td>
								<td></td>
								<td></td>
								</tr>
								<tr height=5%>
								<td colspan=6>&nbsp;</td>
								</tr>
								<tr height=5%>
								<td colspan=6>&nbsp;</td>
								</tr>
								<tr>
								<td colspan=6 style="color:#3D7073; font-size:12px;">&nbsp;&nbsp;Chiller 1</td>
								</tr>
							</table>
							
							
						</div>
						<div style="background-image:url('<?php
						include('SetConnect.php');
						$sql="SELECT MO_C2 from mainTable order by LID desc limit 1";
						$result=mysql_query($sql,$con);
						if($result){
							while($row=mysql_fetch_array($result)){
							if($row['MO_C2']==0)
								echo "images/Icons/Manual/Auto.png";
							else if($row['MO_C2']==1)
								echo "images/Icons/Manual/ON.png";
							else if($row['MO_C2']==2)
								echo "images/Icons/Manual/OFF.png";
							}
						}
					?>'); 	background-repeat: no-repeat; min-height:100px; min-width:110px; font-size:10px; color:#FFFFFF; float:left;">
							<table border=0>
								<tr height=10%>
								<td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
								<td></td>
								<td></td>
								<td></td>
								<td></td>
								<td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
								</tr>
								<tr>
								<tr height=15px>
								<td></td>
								<td></td>
								<td></td>
								<td></td>
								<td></td>
								<td></td>
								</tr>
								<tr>
								<td></td>
								<td></td>
								<td><a href="UpdateAutoC2.php">&nbsp;Auto</a></td>
								<td></td>
								<td><a href="UpdateOnC2.php">On</a></td>
								<td></td>
								</tr>
								<tr >
								<td>&nbsp;</td>
								<td></td>
								<td></td>
								<td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
								<td></td>
								<td></td>
								</tr>
								<tr>
								<td></td>
								<td></td>
								<td></td>
								<td><a href="UpdateOffC2.php">Off</a></td>
								<td></td>
								<td></td>
								</tr>
								<tr height=5%>
								<td colspan=6>&nbsp;</td>
								</tr>
								<tr height=5%>
								<td colspan=6>&nbsp;</td>
								</tr>
								<tr>
								<td colspan=6 style="color:#3D7073; font-size:12px;">&nbsp;&nbsp;Chiller 2</td>
								</tr>
							</table>
							
							
						</div>
						<!--<img src="images/Icons/Manual/Auto.png">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src="images/Icons/Manual/On.png">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src="images/Icons/Manual/off.png">-->
							
				</div>
				<div class="col-md-4" style="width: 120px; text-align:center; color:#3D7073;">
				<!--<h5>STORAGE</h5>
					<div id="canvas">
						
						<div class="circle" id="circles-1"></div> 
						<div class="circle" id="circles-2"></div><br/>
						<table border=0 style="font-size:12px;">
						<tr>
						<td width=110px></td>
						<td>SD Card</td>
						<td width=80px></td>
						<td>Database</td>
						<tr>	
						</table>
					</div>

	<script src="js/circles.js"></script>
	<script>
		var colors = [
				['#DADADA', '#40B3FF'], ['#FCE6A4', '#EFB917'], ['#BEE3F7', '#45AEEA'], ['#F8F9B6', '#D2D558'], ['#F4BCBF', '#D43A43']
			],
			circles = [];

		for (var i = 1; i <= 2; i++) {
			var child = document.getElementById('circles-' + i),
				 
				
				var percentage[] = <?php
					$myFileTin =fopen("sysStatus.txt","r") or die("Unable to open File");
					$members = array();
					while(!feof($myFileTin)){
						$members[]=fgets($myFileTin);
						
					}
					echo $members[5];	
					fclose($myFileTin);?>,	

				
				
				circle = Circles.create({
					id:         child.id,
					value:      percentage[i],
					radius:     getWidth(),
					width:      12,
					colors:     colors[i - 1]
				});
				
				
			circles.push(circle);
			
			
				
				
		}

		window.onresize = function(e) {
			for (var i = 0; i < circles.length; i++) {
				circles[i].updateRadius(getWidth());
			}
		};

		function getWidth() {
			return window.innerWidth / 30;
		}

	</script>
	-->
				</div>
			
				<div class="col-md-4"  style="text-align:center; color:#3D7073; ">
					<h5>INTERFACE STATUS</h5><br/>
					<img src="<?php
					$myFileTin =fopen("sysStatus.txt","r") or die("Unable to open File");
					$members = array();
					while(!feof($myFileTin)){
						$members[]=fgets($myFileTin);
						
					}
						if($members[0]== 0 && $members[1]==0)
							echo "images/Icons/TINTOUT/TOTO.png";
						else if($members[0]== 1 && $members[1]==1)
							echo "images/Icons/TINTOUT/TFTF.png";
						else if($members[0]== 1 && $members[1]==0)
							echo "images/Icons/TINTOUT/TFTO.png";
						else if($members[0]== 0 && $members[1]==1)
							echo "images/Icons/TINTOUT/TOTF.png";
				
					fclose($myFileTin);
				?>">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src="<?php
					$myFileTin =fopen("sysStatus.txt","r") or die("Unable to open File");
					$members = array();
					while(!feof($myFileTin)){
						$members[]=fgets($myFileTin);
						
					}
						if($members[2]== 0 && $members[3]==0)
							echo "images/Icons/DBWEB/DODBO.png";
						else if($members[2]== 1 && $members[3]==1)
							echo "images/Icons/DBWEB/DFDBF.png";
						else if($members[2]== 1 && $members[3]==0)
							echo "images/Icons/DBWEB/DFDBO.png";
						else if($members[2]== 0 && $members[3]==1)
							echo "images/Icons/DBWEB/DODBF.png";
				
					fclose($myFileTin);
				?>">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src="<?php
					$myFileTin =fopen("sysStatus.txt","r") or die("Unable to open File");
					$members = array();
					while(!feof($myFileTin)){
						$members[]=fgets($myFileTin);
						
					}
						if($members[4]== 0)
							echo "images/Icons/GPIO/GPIOO.png";
						else if($members[4]== 1)
							echo "images/Icons/GPIO/GPIOF.png";
						
				
					fclose($myFileTin);
				?>">
				</div>
			</div>
		</div>
	</div>
	<hr/>
		<div class="container-fluid" style="background-color:#FFFFFF;">
		<div class="container jumbotron" style="background-color:#FFFFFF; margin-bottom:0; padding-bottom:0; padding-top:5px;">
			<div class="row" >
				<div class="col-md-6" style="text-align:center; color:#3D7073; ">
              <div id="chartdiv" style="width:100%; height: 450px;"></div>
        </div>
			
				<div class="col-md-6" style="text-align:center; color:#3D7073; ">				
						 <div id="chartdiv1" style="width:100%; height: 450px;"></div>        
				</div>
			</div>
		</div>
	</div>
 <br/>
	<hr/>
 <br/>
 <br/>
	<div class="container-fluid" style="background-color:#FFFFFF;">
		<div class="container jumbotron" style="background-color:#FFFFFF; margin-bottom:0; padding-bottom:0; padding-top:5px;">
			<div class="row" >
				<div class="col-md-5" style="text-align:center; color:#FFFFFF; background-color:#3d7073; min-height:100px; width:45%">
					<div style="width:100%; background-color:#3d7073; padding:10px 10px; font-size:16px;" >
						Firmware Upgrade <br/><br/><form action="updateFirmware.php" method="POST" enctype="multipart/form-data">
						<input type="file" name="file" style="width:350px; float:left;">
						 <input type=submit value=Update name=Update style="color:#000000;" class="btn btn-default">
						</form>
					</div>
				</div>
				<div class="col-md-2" style="text-align:center; color:#FFFFFF;  width:10%">
					
				</div>
				
				<div class="col-md-5" style="text-align:center; color:#FFFFFF; background-color:#3d7073; min-height:100px; width:45%">
					<div style="width:100%; background-color:#3d7073; padding:10px 10px; font-size:16px;" >
						 <br/>
						  Download Log  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="btn btn-default btn-file">
							 <a href="dump.php" style="color:#000000;">View in Excel</a>
							</span>
					</div>
				</div>
			</div>
		</div>
	</div>
	
	<hr/>
    <!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="js/bootstrap.min.js"></script>


  </body>
</html>

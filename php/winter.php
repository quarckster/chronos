<?php
$host = $_SERVER['HTTP_HOST'];
$uri = rtrim(dirname($_SERVER['PHP_SELF']), '/\\');
$extra = 'summer.php';
$home = 'winter.php';
include('SetConnect.php');
?>
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
        $(document).ready(
            function() {
                setInterval(function() {
                    $.get("winter_queries.php", function(data) {
                        $(".system_supply_temp").text(data.system_supply_temp);
                        $(".outlet_temp").text(data.outlet_temp);
                        $(".inlet_temp").text(data.inlet_temp);
                        $(".flue_temp").text(data.flue_temp);
                        $(".cascade_current_power").text(data.cascade_current_power);
                        $(".lead_firing_rate").text(data.lead_firing_rate);
                        $("#outsideTemp").text(data.outsideTemp);
                        $(".returnTemp").text(data.returnTemp);
                        $(".waterOutTemp").text(data.waterOutTemp);
                        $("#setPoint2").text(data.setPoint2);
                        $("#parameterX").text(data.parameterX);
                        $("#t1").text(data.t1);
                        $("#baselineSetPoint").text(data.baselineSetPoint);
                        $("#avgOutsideTemp").text(data.avgOutsideTemp);
                        $("#effectiveSetPoint").text(data.sp);
                        if (data.mode == 0 || data.mode == 2) {
                            $("#winterStatus").attr("src", "images/Icons/WinterSummer/WOn.png");
                            $("#summerStatus").attr("src", "images/Icons/WinterSummer/SOff.png");
                        } else if (data.mode == 1 || data.mode == 3) {
                            $("#winterStatus").attr("src", "images/Icons/WinterSummer/WOff.png");
                            $("#summerStatus").attr("src", "images/Icons/WinterSummer/SOn.png");
                        }
                    }, "json" );
                }, 2000);
            });
   $(function () { 
    $("[data-toggle='tooltip']").tooltip(); 
    });
    </script>   

    <!-- amCharts javascript code -->
        <script type="text/javascript">
          <?php
                        
                        $sql="SELECT returnTemp from mainTable order by LID desc limit 40";
                        $result=mysqli_query($con,$sql);
                        if($result){
                            while($row=mysqli_fetch_array($result,MYSQLI_ASSOC)){
                            $arr[] = $row['returnTemp']; 
                            }
                        }
                    ?>;
     <?php
                        
                        $sql="SELECT logdatetime from mainTable order by LID desc limit 40";
                        $result=mysqli_query($con,$sql);
                        if($result){
                            while($row=mysqli_fetch_array($result,MYSQLI_ASSOC)){
                            $arrDate[] = $row['logdatetime']; 
                            }
                        }
               
                    ?>;
     <?php
                        
                        $sql="SELECT waterOutTemp from mainTable order by LID desc limit 40";
                        $result=mysqli_query($con,$sql);
                        if($result){
                            while($row=mysqli_fetch_array($result,MYSQLI_ASSOC)){
                            $arr1[] = $row['waterOutTemp']; 
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
                            "title": "Water Inlet",
                            "valueField": "column-1"
                        },
            {
                            "bullet": "square",
                            "id": "AmGraph-2",
                            "title": "Water Outlet",
                            "valueField": "column-2"
                        }
                    ],
          "legend": {
                        "useGraphSettings": true
                    },
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
                            "text": "Inlet/Outlet Temperature History"
                        }
                    ],
            "dataProvider": [
            {
              "column-2": <?php echo $arr1[39];?>,
                            "column-1": <?php echo $arr[39];?>,
                            "date": "<?php echo substr($arrDate[39],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[38];?>,
                            "column-1": <?php echo $arr[38];?>,
                            "date": "<?php echo substr($arrDate[38],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[37];?>,
                            "column-1": <?php echo $arr[37];?>,
                            "date": "<?php echo substr($arrDate[36],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[36];?>,
                            "column-1": <?php echo $arr[36];?>,
                            "date": "<?php echo substr($arrDate[36],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[35];?>,
                            "column-1": <?php echo $arr[35];?>,
                            "date": "<?php echo substr($arrDate[35],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[34];?>,
                            "column-1": <?php echo $arr[34];?>,
                            "date": "<?php echo substr($arrDate[34],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[33];?>,
                            "column-1": <?php echo $arr[33];?>,
                            "date": "<?php echo substr($arrDate[33],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[32];?>,
                            "column-1": <?php echo $arr[32];?>,
                            "date": "<?php echo substr($arrDate[32],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[31];?>,
                            "column-1": <?php echo $arr[31];?>,
                            "date": "<?php echo substr($arrDate[31],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[30];?>,
                            "column-1": <?php echo $arr[30];?>,
                            "date": "<?php echo substr($arrDate[30],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[29];?>,
                            "column-1": <?php echo $arr[29];?>,
                            "date": "<?php echo substr($arrDate[29],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[28];?>,
                            "column-1": <?php echo $arr[28];?>,
                            "date": "<?php echo substr($arrDate[28],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[27];?>,
                            "column-1": <?php echo $arr[27];?>,
                            "date": "<?php echo substr($arrDate[27],0,16);?>"
                        },
            {
              "column-2": <?php echo $arr1[26];?>,
                            "column-1": <?php echo $arr[26];?>,
                            "date": "<?php echo substr($arrDate[26],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[25];?>,
                            "column-1": <?php echo $arr[25];?>,
                            "date": "<?php echo substr($arrDate[25],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[24];?>,
                            "column-1": <?php echo $arr[24];?>,
                            "date": "<?php echo substr($arrDate[24],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[23];?>,
                            "column-1": <?php echo $arr[23];?>,
                            "date": "<?php echo substr($arrDate[23],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[22];?>,
                            "column-1": <?php echo $arr[22];?>,
                            "date": "<?php echo substr($arrDate[22],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[21];?>,
                            "column-1": <?php echo $arr[21];?>,
                            "date": "<?php echo substr($arrDate[21],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[20];?>,
                            "column-1": <?php echo $arr[20];?>,
                            "date": "<?php echo substr($arrDate[20],0,16);?>"
                        },
            {
              "column-2": <?php echo $arr1[19];?>,
                            "column-1": <?php echo $arr[19];?>,
                            "date": "<?php echo substr($arrDate[19],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[18];?>,
                            "column-1": <?php echo $arr[18];?>,
                            "date": "<?php echo substr($arrDate[18],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[17];?>,
                            "column-1": <?php echo $arr[17];?>,
                            "date": "<?php echo substr($arrDate[17],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[16];?>,
                            "column-1": <?php echo $arr[16];?>,
                            "date": "<?php echo substr($arrDate[16],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[15];?>,
                            "column-1": <?php echo $arr[15];?>,
                            "date": "<?php echo substr($arrDate[15],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[14];?>,
                            "column-1": <?php echo $arr[14];?>,
                            "date": "<?php echo substr($arrDate[14],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[13];?>,
                            "column-1": <?php echo $arr[13];?>,
                            "date": "<?php echo substr($arrDate[13],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[12];?>,
                            "column-1": <?php echo $arr[12];?>,
                            "date": "<?php echo substr($arrDate[12],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[11];?>,
                            "column-1": <?php echo $arr[11];?>,
                            "date": "<?php echo substr($arrDate[11],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[10];?>,
                            "column-1": <?php echo $arr[10];?>,
                            "date": "<?php echo substr($arrDate[10],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[9];?>,
                            "column-1": <?php echo $arr[9];?>,
                            "date": "<?php echo substr($arrDate[9],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[8];?>,
                            "column-1": <?php echo $arr[8];?>,
                            "date": "<?php echo substr($arrDate[8],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[7];?>,
                            "column-1": <?php echo $arr[7];?>,
                            "date": "<?php echo substr($arrDate[7],0,16);?>"
                        },
            {
              "column-2": <?php echo $arr1[6];?>,
                            "column-1": <?php echo $arr[6];?>,
                            "date": "<?php echo substr($arrDate[6],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[5];?>,
                            "column-1": <?php echo $arr[5];?>,
                            "date": "<?php echo substr($arrDate[5],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[4];?>,
                            "column-1": <?php echo $arr[4];?>,
                            "date": "<?php echo substr($arrDate[4],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[3];?>,
                            "column-1": <?php echo $arr[3];?>,
                            "date": "<?php echo substr($arrDate[3],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[2];?>,
                            "column-1": <?php echo $arr[2];?>,
                            "date": "<?php echo substr($arrDate[2],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[1];?>,
                            "column-1": <?php echo $arr[1];?>,
                            "date": "<?php echo substr($arrDate[1],0,16);?>"
                        },
                        {
              "column-2": <?php echo $arr1[0];?>,
                            "column-1": <?php echo $arr[0];?>,
                            "date": "<?php echo substr($arrDate[0],0,16);?>"
                        }
   
                    ]
                }
            );
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
                    $myFileSys =fopen("systemUp.txt","r") or die("Unable to open File");
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
                        <img id="winterStatus" src=""/><br/><a href="updateModeOn.php" font-size:10px;">Winter</a>
                        </div>
                    
                    <div style="min-width:80px; font-size:10px; color:"#FFFFFF"; float:"left"; text-align="center";">
                        <img id="summerStatus" src=""/><br/><a href="updateModeOff.php" style="color:#FFFFFF; font-size:10px;">Summer</a>
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
                    <b>Winter Mode</b>
                    </div>
                    <br/>
                    <h5 id="OutsideTemp" style="font-size:15px;">
          <table align=center>
          <tr>
          <td align=left>Wind Chill</td>
                    <td><span id="outsideTemp"></span> &deg;F</td></tr>
          <tr></tr>   
          <tr>      
             <td>Avg Wind Chill (96 hrs)&nbsp;&nbsp;&nbsp;&nbsp; </td>
                    <td><span id="avgOutsideTemp"></span> &deg;F</td>
          </tr>
          </table></h5> 
    
                        <!--Dynamic Content-->
                    <h6><small style="color:#FFFFFF;"><a href="http://wx.thomaslivestock.com" style="color:#FFFFFF;">wx.thomaslivestock.com</a></small></h6>
                        <div style="height:5px;"></div>
                    <h5 align=left><b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ModBus</b></h5>
                    <table  align=center border=0>
                <tr>
                        <td width=170px align=left>System Supply Temp</td>
                        <td width=80px><span class="system_supply_temp"></span>  &deg;F</td><!--Dynamic Content-->
                        </tr>
                <tr>
                        <td width=170px align=left>Outlet Temp</td>
                        <td width=80px><span class="outlet_temp"></span>  &deg;F</td><!--Dynamic Content-->
                        </tr>
                <tr>
                        <td width=170px align=left>Inlet Temp</td>
                        <td width=80px><span class="inlet_temp"></span>  &deg;F</td><!--Dynamic Content-->
                        </tr>      
                        <tr>
                        <td width=170px align=left>Cascade Power</td>
                        <td width=80px><span class="cascade_current_power"></span> %</td><!--Dynamic Content-->
                        </tr>
                        <tr>
                        <td align=left>Lead Firing Rate</td>
                        <td><span class="lead_firing_rate"></span> %</td><!--Dynamic Content-->
                        </tr>
                        
                    </table>
                    <div style="height:15px;"></div>
                    <h5 align=left><b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Sensors</b></h5>
                    <table  align=center border=0>
                        <tr>
                        <td width=170px align=left>Inlet</td>
                        <td width=80px><span class="returnTemp"></span> &deg;F</td><!--Dynamic Content-->
                        </tr>
                        <tr>
                        <td align=left>Outlet</td>
                        <td><span class="waterOutTemp"></span> &deg;F</td><!--Dynamic Content-->
                        </tr>
                        
                    </table>
                
                    <br/>
                    <br/>
               
                </div>
                </div>
                <!-- <div id=Just data-toggle="tooltip" data-placement="down" data-original-title="<?php
                        
                        if($result1){
                            if($row1['mode'] == 0 or $row1['mode'] == 2)
                                echo "Effective Setpoint = Dynamic Setpoint + Boiler Offset";
                            else if($row1['mode'] == 1 or $row1['mode'] == 3)
                                echo "Effective Setpoint = Dynamic Setpoint + Chiller1 Offset";
                        }
                    ?>" style="position:absolute; z-index:100; right:180px; top:270px; min-height:40px; min-width:60px;">
            
        </div> -->
                <div class="col-md-6" id="updateImage" style="text-align:center; color:#FFFFFF; min-height:300px;">
                    <div  id="insideImage" style="width:100%; margin-top:30px; padding:10px 10px; font-size:11px; background-repeat:"no-repeat"; min-height:300px;" >
               <div  style="float:left;">
                     &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;
                     </div> 
                     <div min-width=250px style="float:left;">
                     
                     </div>
                         <div style="float:left;"><table border="0" >
                            <tr height=50px>
                            <td width=60px></td>
                                <td></td>
                                <td></td>
                                <td></td>
                              <td></td>
                            <tr>
                            <tr>
                            <td></td>
                                <td></td>   
                                <td></td>
                                <td></td>
                                <td ></td>
                            <tr>
                            <tr>
                <td></td>
                                <td></td>
                                <td></td>
                                <td></td>
                                <td></td>
                            
                            <tr>
                            <tr>
                  <td></td>                
                                <td></td>
                                <td></td>   
                                <td></td>
                                <td></td>
                            
                            <tr>
                            <tr>
              <td></td>
                                <td><br/><img src="<?php
                        
                        $sql="SELECT status from actStream where TID=1";
                        $result=mysqli_query($con,$sql);
                        if($result){
                            while($row=mysqli_fetch_array($result,MYSQLI_ASSOC)){
                            if ($row['status']==1)
                                echo "images/Icons/Boiler/Boiler-ON.png"; 
                            else if ($row['status']==0)
                                echo "images/Icons/Boiler/Boiler-OFF.png"; 
                            
                            }
                        }
                    ?>" style="z-index:-1; position:static;" />
          <p style="margin-top:-180px; color:#000000; font-size:15px;"><b>Cascade Fire</b><br/>
          <span class="cascade_current_power"></span> %
             <br/>
             <br/>
             <b>Lead Fire</b><br/>
          <span class="lead_firing_rate"></span> %
          </p>
          </td>
                                
                            
                        </tr>
                        </table></div>
                <div width=100px style="float:left;">
                <br/><br/><br/><br/><br/><span class="outlet_temp"></span> &deg;F    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <span class="system_supply_temp"></span> &deg;F
          <br/>
                <img src="images/Icons/Boiler/arrow4.png" /><br/>
                <span class="waterOutTemp"></span> &deg;F
             <br/><br/><br/><br/><br/><span class="inlet_temp"></span> &deg;F &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <br/>
                <img src="images/Icons/Boiler/arrow3.png" /><br/>
                <span class="returnTemp"></span> &deg;F 
                     </div>     
                    </div>
                    
                </div>
            
                <div class="col-md-3" style="text-align:center; color:#FFFFFF; background-color:#224042; padding:0 0; min-height:360px;">
            
            

                    <div style="width:100%; background-color:#FF6600; padding:10px 10px;" >
                    <b>User Settings</b>
                    </div>
                <br/>
                <div id="updateSetpointtwo">
                <div  id="insidetwo" style="text-align:center; color:#FFFFFF; background-color:#224042; padding:0 0;">
                    
                    <h5 id="OutsideTemp" style="font-size:15px;">
              <br/>
              <br/>
          <table align=center border=0><tr>
          <td align=left width=180px>Baseline Setpoint &nbsp;</td>
                    <td><span id="baselineSetPoint"></span> &deg;F</td>      <!--Dynamic Content-->
           </tr>
           <tr>
           <td>&nbsp;</td>
           <td></td>
           </tr><tr>  
                    <td align=left>THA Setpoint</td>
          <td> <span id="setPoint2"></span> &deg;F</td>
            </tr>
            <tr>
           <td>&nbsp;</td>
           <td></td>
           </tr><tr> 
                    <td align=left>Effective Setpoint</td>
          <td>  <span id="effectiveSetPoint"></span> &deg;F </small></td>
        </tr>
        
        </table></h5>
                <br/>
        <br/>
        <br/>
    </div>
</div>                  
          <hr/ style="opacity:0.5;">
<div>
  <div>
       <form name="UpdateParameter" action="UpdatePara.php" method=post>

      
              <br/>
               <br/>
                    
                    <table border=0 align=center>
                        
                        <tr>
                        <td>Setpoint Offset</td>
                        <td width=5%></td>
                        <td><span id="parameterX"></span> &deg;F</td>
            <td width=10px></td>
                        <td style="color:#000000;"><input type="text" name="parameterX" size=2></td><!--Dynamic Content-->
                        <td width=3%></td>
                        <td><input type="Submit" value="Update" style="color:#000000;"></td>
                        </tr>
            <tr>
                        <td>Tolerance</td>
                        <td width=5%></td>
                        <td><span id="t1"></span> &deg;F</td><td ></td>
                        <td style="color:#000000;"><input type="text" name="t1" size=2></td><!--Dynamic Content-->
                        <td width=3%></td>
                        <td><input type="Submit" value="Update" style="color:#000000;"></td>
                        </tr>
                        
                    </table>
    <br/>   <br/>
    </form>
    </div>
</div> 
        
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
                    <h6 id="OutsideTemp">OFFLINE</h6>   --> <!--Dynamic Content-->
                    
                </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="container-fluid" id="updateInterface" style="background-color:#FFFFFF;">
        <div class="container jumbotron" id="insideInterface" style="background-color:#FFFFFF; margin-bottom:0; padding-bottom:0; padding-top:5px;">
            <div class="row" >
                <div class="col-md-4" style="width:50px; text-align:center; color:#3D7073;">
                </div>
                <div class="col-md-6" style="text-align:center; color:#3D7073; ">
                    <h5>MANUAL OVERRIDE</h5><br/>
                    <div style="min-height:100px; min-width:35px; float:left;">
                            
                        </div>
                        <div style="background-image:url('<?php
                        
                        $sql="SELECT MO_B from mainTable order by LID desc limit 1";
                        $result=mysqli_query($con,$sql);
                        if($result){
                            while($row=mysqli_fetch_array($result,MYSQLI_ASSOC)){
                            if($row['MO_B']==0)
                                echo "images/Icons/Manual/Auto.png";
                            else if($row['MO_B']==1)
                                echo "images/Icons/Manual/ON.png";
                            else if($row['MO_B']==2)
                                echo "images/Icons/Manual/OFF.png";
                            }
                        }
                    ?>');   background-repeat: no-repeat; min-height:100px; min-width:110px; font-size:10px; color:#FFFFFF; float:left;">
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
                        
                        $sql="SELECT MO_C1 from mainTable order by LID desc limit 1";
                        $result=mysqli_query($con,$sql);
                        if($result){
                            while($row=mysqli_fetch_array($result,MYSQLI_ASSOC)){
                            if($row['MO_C1']==0)
                                echo "images/Icons/Manual/Auto.png";
                            else if($row['MO_C1']==1)
                                echo "images/Icons/Manual/ON.png";
                            else if($row['MO_C1']==2)
                                echo "images/Icons/Manual/OFF.png";
                            }
                        }
                    ?>');   background-repeat: no-repeat; min-height:100px; min-width:110px; font-size:10px; color:#FFFFFF; float:left;">
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
                        
                        $sql="SELECT MO_C2 from mainTable order by LID desc limit 1";
                        $result=mysqli_query($con,$sql);
                        if($result){
                            while($row=mysqli_fetch_array($result,MYSQLI_ASSOC)){
                            if($row['MO_C2']==0)
                                echo "images/Icons/Manual/Auto.png";
                            else if($row['MO_C2']==1)
                                echo "images/Icons/Manual/ON.png";
                            else if($row['MO_C2']==2)
                                echo "images/Icons/Manual/OFF.png";
                            }
                        }
                    ?>');   background-repeat: no-repeat; min-height:100px; min-width:110px; font-size:10px; color:#FFFFFF; float:left;">
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
                      <div style="background-image:url('<?php
                        
                        $sql="SELECT MO_C3 from mainTable order by LID desc limit 1";
                        $result=mysqli_query($con,$sql);
                        if($result){
                            while($row=mysqli_fetch_array($result,MYSQLI_ASSOC)){
                            if($row['MO_C3']==0)
                                echo "images/Icons/Manual/Auto.png";
                            else if($row['MO_C3']==1)
                                echo "images/Icons/Manual/ON.png";
                            else if($row['MO_C3']==2)
                                echo "images/Icons/Manual/OFF.png";
                            }
                        }
                    ?>');   background-repeat: no-repeat; min-height:100px; min-width:110px; font-size:10px; color:#FFFFFF; float:left;">
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
                                <td><a href="UpdateAutoC3.php">&nbsp;Auto</a></td>
                                <td></td>
                                <td><a href="UpdateOnC3.php">On</a></td>
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
                                <td><a href="UpdateOffC3.php">Off</a></td>
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
                                <td colspan=6 style="color:#3D7073; font-size:12px;">&nbsp;&nbsp;Chiller 3</td>
                                </tr>
                            </table>
                            
                            
                        </div>
                      <div style="background-image:url('<?php
                        
                        $sql="SELECT MO_C4 from mainTable order by LID desc limit 1";
                        $result=mysqli_query($con,$sql);
                        if($result){
                            while($row=mysqli_fetch_array($result,MYSQLI_ASSOC)){
                            if($row['MO_C4']==0)
                                echo "images/Icons/Manual/Auto.png";
                            else if($row['MO_C4']==1)
                                echo "images/Icons/Manual/ON.png";
                            else if($row['MO_C4']==2)
                                echo "images/Icons/Manual/OFF.png";
                            }
                        }
                    ?>');   background-repeat: no-repeat; min-height:100px; min-width:110px; font-size:10px; color:#FFFFFF; float:left;">
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
                                <td><a href="UpdateAutoC4.php">&nbsp;Auto</a></td>
                                <td></td>
                                <td><a href="UpdateOnC4.php">On</a></td>
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
                                <td><a href="UpdateOffC4.php">Off</a></td>
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
                                <td colspan=6 style="color:#3D7073; font-size:12px;">&nbsp;&nbsp;Chiller 4</td>
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
                
        <div class="col-md-6" style="text-align:center; color:#3D7073; width:100%">
              <div id="chartdiv" style="width:100%; height: 450px;"></div>
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
                <div class="col-md-2" style="text-align:center; color:#FFFFFF; width:10%">
                    
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

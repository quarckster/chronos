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
    <script type="text/javascript" src="inc/TimeCircles.js"></script>
    <link rel="stylesheet" href="inc/TimeCircles.css" />
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
        <div class="container">
            <h2>Please wait for 2 minutes to complete the switch over</h2>
            <div id="CountDownTimer" data-timer="120" style="width: 1000px; height: 250px;"></div>
        </div>
        <script>
            function makeAjaxRequest(mode) {
                $.ajax({
                   type: "GET",
                   url: "switch_mode.php?mode=" + mode
                });
            }
            makeAjaxRequest(3);
            $("#CountDownTimer").TimeCircles({ time: { Days: { show: false }, Hours: { show: false } },
                             animation: "ticks",
                             count_past_zero: false
            })
            .addListener(function(unit, value, total) {
                if(total <= 1) {
                    makeAjaxRequest(1);
                }
                if(total <= 0) {
                    window.location.replace("summer.php");
                }
            });
        </script>       
    </body>
</html>
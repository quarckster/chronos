<?php
include('SetConnect.php');
$sql = "UPDATE mainTable SET mode=".$_GET['mode']." ORDER BY LID DESC LIMIT 1";
$result = mysqli_query($con, $sql);
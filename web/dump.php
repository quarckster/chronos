<?php

include('SetConnect.php');

//header to give the order to the browser
header('Content-Type: text/csv');
header('Content-Disposition: attachment;filename=exported-data.csv');

//select table to export the data
$sql="select * from mainTable ORDER BY LID DESC";
$result=mysqli_query($con,$sql);
$rows=mysqli_fetch_array($result,MYSQLI_ASSOC);

if ($rows)
{
getcsv(array_keys($rows));
}
while($rows)
{
 getcsv($rows);
 $rows = mysqli_fetch_array($result,MYSQLI_ASSOC);
}

// get total number of fields present in the database
function getcsv($no_of_field_names)
{
$separate = '';


// do the action for all field names as field name
foreach ($no_of_field_names as $field_name)
{
if (preg_match('/\\r|\\n|,|"/', $field_name))
{
$field_name = '' . str_replace('', $field_name) . '';
}
echo $separate . $field_name;

//sepearte with the comma
$separate = ',';
}

//make new row and line
echo "\r\n";
}
?>
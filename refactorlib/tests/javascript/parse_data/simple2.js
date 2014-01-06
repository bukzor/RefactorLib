// From: http://technotip.com/165/fibonacci-series-javascript/
var var1 = 0;
var var2 = 1;
var var3;

var num = prompt("Enter the limit to generate fibonacci no",0);

document.write(var1+"<br />");
document.write(var2+"<br />");

for(var i=3; i <= num;i++)
{
    var3 = var1 + var2;
    var1 = var2;
    var2 = var3;

    document.write(var3+"<br />");
}

// fooo


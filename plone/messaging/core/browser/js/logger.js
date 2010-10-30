var BOSH_SERVICE = 'http://localhost:8080/http-bind/'
var connection = null;

function log(msg) 
{
    $('#log').append('<div></div>').append(document.createTextNode(msg));
}

function rawInput(data)
{
    log('RECV: ' + data);
}

function rawOutput(data)
{
    log('SENT: ' + data);
}

$(document).ready(function () {
    //connection = new Strophe.Connection(BOSH_SERVICE);
    connection.rawInput = rawInput;
    connection.rawOutput = rawOutput;


});
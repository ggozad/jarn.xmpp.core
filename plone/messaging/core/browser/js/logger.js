
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
    pmcxmpp.connection.rawInput = rawInput;
    pmcxmpp.connection.rawOutput = rawOutput;
});
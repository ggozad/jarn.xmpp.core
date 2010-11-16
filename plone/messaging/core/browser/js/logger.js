pmcxmpp.log = function (msg) 
{
    $('#log').append('<div></div><br/>').append(document.createTextNode(msg));
}

pmcxmpp.rawInput = function(data)
{
    pmcxmpp.log('RECV: ' + data);
}

pmcxmpp.rawOutput = function (data)
{
    pmcxmpp.log('SENT: ' + data);
}

$(document).bind('pmcxmpp.connected', function () {
    pmcxmpp.connection.rawInput = pmcxmpp.rawInput;
    pmcxmpp.connection.rawOutput = pmcxmpp.rawOutput;
});
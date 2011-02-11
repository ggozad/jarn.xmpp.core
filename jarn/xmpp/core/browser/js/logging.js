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

jarnxmpp.log = function (msg) 
{
	$('#log').append('<div></div><br/>').append(document.createTextNode(msg));
}

jarnxmpp.rawInput = function(data)
{
	jarnxmpp.log('RECV: ' + data);
}

jarnxmpp.rawOutput = function (data)
{
	jarnxmpp.log('SENT: ' + data);
}

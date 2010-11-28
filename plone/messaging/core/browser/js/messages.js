$(document).bind('pmcxmpp.message', function (event) {
	//XXX If mtype is 'xhtml' we should sanitize
	$("#pcmxmpp-messages").notify("create",
	{
	    title: event.from,
	    text: event.body
	},
	{
		expires: false
	});		
});

$(document).ready(function () {
	$('#pcmxmpp-messages').notify();
});

$(document).bind('pmcxmpp.message', function (event) {
    var div = $('<div></div>');
	from = event.from;
	message = event.body;
    $(message).each(function () {
		$("#pcmxmpp-messages").notify("create",
		{
		    title: from,
		    text: this.data
		},
		{
			expires: false
		});
    });
});

$(document).ready(function () {
	$('#pcmxmpp-messages').notify();
});

$(document).bind('pmcxmpp.message', function (event, message) {
    var div = $('<div></div>');
    $(message).each(function () {
		$("#pcmxmpp-messages").notify("create", {
		    title: 'Notification',
		    text: this.data
		});
    });
});

$(document).ready(function () {
	$('#pcmxmpp-messages').notify();
});

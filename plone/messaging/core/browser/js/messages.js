$(document).bind('pmcxmpp.message', function (event) {
	//XXX If mtype is 'xhtml' we should sanitize
	$.gritter.add({
		title: event.from,
		text: event.body,
	});
});

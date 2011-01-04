$(document).bind('pmcxmpp.nodePublished', function (event) {
	//XXX If mtype is 'xhtml' we should sanitize
	$.gritter.add({
		title: event.author,
		text: event.content,
		image: portal_url+'/portal_memberdata/portraits/'+event.author,
	});
});

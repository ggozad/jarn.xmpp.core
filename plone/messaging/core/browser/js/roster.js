$(document).bind('pmcxmpp.connected', function () {
	var roster_iq = $iq({type: 'get'}).c('query', {xmlns: Strophe.NS.ROSTER});
	pmcxmpp.connection.sendIQ(roster_iq, function (iq) {
		alert(iq['body']);
	});
});
pmcxmpp.onConnect = function (status) {
	if ((status === Strophe.Status.ATTACHED) ||
	    (status === Strophe.Status.CONNECTED)) {
		$(window).bind('beforeunload', function() {
			pmcxmpp.connection.flush();
			pmcxmpp.connection.disconnect();
		});
		$(document).trigger('pmcxmpp.connected');
		
	} else if (status === Strophe.Status.DISCONNECTED) { 
		$(document).trigger('pmcxmpp.disconnected');
	}
};

$(document).ready(function () {
	pmcxmpp.connection = new Strophe.Connection(pmcxmpp.BOSH_SERVICE);
	if (('rid' in pmcxmpp) && ('sid' in pmcxmpp))
		pmcxmpp.connection.attach(pmcxmpp.jid, pmcxmpp.sid, pmcxmpp.rid, pmcxmpp.onConnect);
	else 
		pmcxmpp.connection.connect(pmcxmpp.jid, pmcxmpp.password, pmcxmpp.onConnect);
});

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

pmcxmpp.Messages = {
	messageReceived: function (message) {
		var body = $(message).children('body').text();
		if (body=="") {
			return true; // This is a typing notification, we do not handle it here...
		}
		var xhtml_body = $(message).find('html > body').contents();
		event = jQuery.Event('pmcxmpp.message');

		if (xhtml_body.length>0) {
			event.mtype = 'xhtml';
			event.body = xhtml_body.html();
		} else {
			event.body = body;
			event.mtype = 'text'
		}
		event.from = $(message).attr('from');
		$(document).trigger(event);
		return true;
	}
};

pmcxmpp.Roster = {
	rosterSet: function(iq) {
		// XXX: Fill me in
	},
	rosterResult: function(iq) {
		// XXX: Fill me in
	}
};

pmcxmpp.Presence = {
	presenceReceived: function (presence) {
		var ptype = $(presence).attr('type');
		var from = $(presence).attr('from');
		var status = '';
		if (ptype !== 'error') {
			if (ptype === 'unavailable') {
				status = 'offline';
			} else {
				var show = $(presence).find('show').text(); 
				if (show === '' || show === '') {
					status = 'online'
				} else {
					status = 'away'
				}
			}
			$(document).trigger('pmcxmpp.presence', [from, status]);
		}
		return true;
	}
};



$(document).bind('pmcxmpp.connected', function () {
	// Logging
	pmcxmpp.connection.rawInput = pmcxmpp.rawInput;
	pmcxmpp.connection.rawOutput = pmcxmpp.rawOutput;

	// Messages
	pmcxmpp.connection.addHandler(pmcxmpp.Messages.messageReceived,
								  null, 'message', 'chat');
	//Roster
	pmcxmpp.connection.addHandler(pmcxmpp.Roster.rosterSet, Strophe.NS.ROSTER, 'iq', 'set');
	pmcxmpp.connection.addHandler(pmcxmpp.Roster.rosterResult, Strophe.NS.ROSTER, 'iq', 'result');
	//var roster_iq = $iq({type: 'get'}).c('query', {xmlns: Strophe.NS.ROSTER});
	//pmcxmpp.connection.sendIQ(roster_iq);
	// Presence
	pmcxmpp.connection.addHandler(pmcxmpp.Presence.presenceReceived, null, 'presence', null);
	pmcxmpp.connection.send($pres());
});

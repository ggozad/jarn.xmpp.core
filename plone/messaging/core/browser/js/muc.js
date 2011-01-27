pmcxmpp.muc = {
	room: 'myroom@conference.localhost',
	nickname: null,
	NS_MUC: "http://jabber.org/protocol/muc",

    joined: null,
    participants: null,

	presenceReceived: function (presence) {
		
	}
};

$(document).bind('pmcxmpp.connected', function () {
	// Logging
	pmcxmpp.connection.rawInput = pmcxmpp.rawInput;
	pmcxmpp.connection.rawOutput = pmcxmpp.rawOutput;
	// Room creation
	pmcxmpp.nickname = Strophe.getNodeFromJid(pmcxmpp.jid);
	pmcxmpp.connection.send(
		$pres({
			to: pmcxmpp.muc.room+'/'+pmcxmpp.nickname
		}).c('x', {xmlns: pmcxmpp.muc.NS_MUC}));
	
});
pmcxmpp.Presence = {
};

$(document).bind('pmcxmpp.connected', function () {
	pmcxmpp.connection.send($pres());
});

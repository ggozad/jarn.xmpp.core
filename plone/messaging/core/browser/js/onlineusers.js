$(document).bind('pmcxmpp.presence', function (event, jid, status) {
	jid = Strophe.getBareJidFromJid(jid);
	existing = $('#online-users dd').find(":contains("+jid+")");
	existing.parent().remove()
	dd = $('<dd></dd>').addClass("portletItem");
	dd.append($('<span></span>').addClass(status).text(jid));
	$('#online-users').append(dd);
});

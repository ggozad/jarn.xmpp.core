//var BOSH_SERVICE = 'http://localhost:8080/http-bind/'
//var connection = null;

function onConnect(status)
{
}

$(document).ready(function () {
    pmcxmpp.connection = new Strophe.Connection(pmcxmpp.BOSH_SERVICE);
	pmcxmpp.connection.connect(pmcxmpp.jid, pmcxmpp.password, onConnect);
});
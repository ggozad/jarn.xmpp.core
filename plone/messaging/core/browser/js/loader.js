pmcxmpp.onConnect = function (status) {
    if (status === Strophe.Status.CONNECTED) {
        $(document).trigger('pmcxmpp.connected');
    } else if (status === Strophe.Status.DISCONNECTED) { 
        $(document).trigger('pmcxmpp.disconnected');
    }
};

$(document).ready(function () {
    pmcxmpp.connection = new Strophe.Connection(pmcxmpp.BOSH_SERVICE);
    pmcxmpp.connection.connect(pmcxmpp.jid, pmcxmpp.password, pmcxmpp.onConnect);
});

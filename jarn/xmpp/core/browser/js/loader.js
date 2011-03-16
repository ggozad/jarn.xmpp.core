jarnxmpp.onConnect = function (status) {
    if ((status === Strophe.Status.ATTACHED) ||
        (status === Strophe.Status.CONNECTED)) {
        $(window).bind('beforeunload', function() {
            jarnxmpp.connection.flush();
            jarnxmpp.connection.disconnect();
        });
        $(document).trigger('jarnxmpp.connected');
    } else if (status === Strophe.Status.DISCONNECTED) {
        $(document).trigger('jarnxmpp.disconnected');
    }
};

$(document).ready(function () {
    jarnxmpp.connection = new Strophe.Connection(jarnxmpp.BOSH_SERVICE);
    if (('rid' in jarnxmpp) && ('sid' in jarnxmpp))
        jarnxmpp.connection.attach(jarnxmpp.jid, jarnxmpp.sid, jarnxmpp.rid, jarnxmpp.onConnect);
    else
        jarnxmpp.connection.connect(jarnxmpp.jid, jarnxmpp.password, jarnxmpp.onConnect);
});

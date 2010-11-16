pmcxmpp.Messages = {
    gotMessage: function (message) {
        var body = $(message).find('body').contents();
        var div = $("<div></div>");
        body.each(function () {
            if (document.importNode) {
                $(document.importNode(this, true)).appendTo(div);
            } else {
                // IE workaround
                div.append(this.xml);
            }
        });
        div.prependTo('#pcmxmpp-messages');
        return true;
    }
};
$(document).bind('pmcxmpp.connected', function () {
    pmcxmpp.connection.addHandler(pmcxmpp.Messages.gotMessage,
                                  null, 'message', 'chat');
});

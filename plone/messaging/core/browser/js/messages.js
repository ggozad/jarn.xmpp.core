$(document).bind('pmcxmpp.message', function (event, message) {
    var div = $('<div></div>');
    $(message).each(function () {
        if (document.importNode) {
            $(document.importNode(this, true)).appendTo(div);
        } else {
            // IE workaround
            div.append(this.xml);
        }
    });
    $(div).prependTo('#pcmxmpp-messages');
});

pmcxmpp.muc = {
    room: 'myroom@conference.localhost',
    nickname: null,
    NS_MUC: "http://jabber.org/protocol/muc",

    joined: null,
    participants: null,

    presenceReceived: function (presence) {
        var from = $(presence).attr('from');
        var room = Strophe.getBareJidFromJid(from);
        // Is this for us?
        if (room != pmcxmpp.muc.room) return true;
        var nick = Strophe.getResourceFromJid(from);

        if ($(presence).attr('type') !== 'error' &&
            !pmcxmpp.muc.joined) {
            // check for status 110 to see if we joined or created
            // the room
            if (($(presence).find("status[code='110']").length > 0) ||
                ($(presence).find("status[code='201']").length > 0)) {
                // check if server changed our nick
                if ($(presence).find("status[code='210']").length > 0) {
                    pmcxmpp.muc.nickname = Strophe.getResourceFromJid(from);
                }
                // room join complete
                $(document).trigger("pmcxmpp.muc.roomJoined");
            }
        }

        return true;

    },

    addMessage: function (msg) {
        // detect if we are scrolled all the way down
        var chat = $('#chat').get(0);
        var at_bottom = chat.scrollTop >= chat.scrollHeight -
            chat.clientHeight;
        $('#chat').append(msg);
        // if we were at the bottom, keep us at the bottom
        if (at_bottom) {
            chat.scrollTop = chat.scrollHeight;
        }
    }
};

$(document).bind('pmcxmpp.connected', function () {
    // Logging
    pmcxmpp.connection.rawInput = pmcxmpp.rawInput;
    pmcxmpp.connection.rawOutput = pmcxmpp.rawOutput;
    // Presence
    pmcxmpp.connection.addHandler(pmcxmpp.muc.presenceReceived,
                                  null, "presence");
    // Room creation
    pmcxmpp.nickname = Strophe.getNodeFromJid(pmcxmpp.jid);
    pmcxmpp.connection.send(
        $pres({
            to: pmcxmpp.muc.room+'/'+pmcxmpp.nickname
        }).c('x', {xmlns: pmcxmpp.muc.NS_MUC}));

});

$(document).bind('pmcxmpp.muc.roomJoined', function () {
    pmcxmpp.muc.joined = true;
    $('#room-name').text(pmcxmpp.muc.room);

    pmcxmpp.muc.addMessage("<div class='notice'>*** Room joined.</div>")
});

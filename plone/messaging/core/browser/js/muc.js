pmcxmpp.muc = {
    NS_MUC: "http://jabber.org/protocol/muc",
    room: 'myroom1@conference.localhost',
    nickname: null,
    joined: null,
    participants: null,

    presenceReceived: function (presence) {
        var from = $(presence).attr('from');
        var room = Strophe.getBareJidFromJid(from);
        // Is this for us?
        if (room != pmcxmpp.muc.room) return true;
        var nick = Strophe.getResourceFromJid(from);

        if (!pmcxmpp.muc.participants[nick] &&
            $(presence).attr('type') !== 'unavailable') {

            // add to participant list
            var user_jid = $(presence).find('item').attr('jid');
            pmcxmpp.muc.participants[nick] = user_jid || true;

            if (pmcxmpp.muc.joined) {
                $(document).trigger('pmcxmpp.muc.userJoined', nick);
            }
        } else if (pmcxmpp.muc.participants[nick] &&
                   $(presence).attr('type') === 'unavailable') {
            delete pmcxmpp.muc.participants[nick];
            $(document).trigger('pmcxmpp.muc.userLeft', nick);
        }

        if ($(presence).attr('type') !== 'error' &&
                   !pmcxmpp.muc.joined) {
            // check for status 110 or 201 to see if we joined or created
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
        } else if ($(presence).attr('type') === 'error' &&
                   !pmcxmpp.muc.joined) {
            // error joining room
            pmcxmpp.connection.disconnect();
        }
        return true;
    },

    publicMessageReceived: function (message) {
        var from = $(message).attr('from');
        var room = Strophe.getBareJidFromJid(from);
        var nick = Strophe.getResourceFromJid(from);
        if (room != pmcxmpp.muc.room) return true;

        var notice = !nick;

        // messages from ourself will be styled differently
        var nick_class = "nick";
        if (nick === pmcxmpp.muc.nickname) {
            nick_class += " self";
        }

        var body = $(message).children('body').text();

        var delayed = $(message).children("delay").length > 0  ||
            $(message).children("x[xmlns='jabber:x:delay']").length > 0;

        // look for room topic change
        var subject = $(message).children('subject').text();
        if (subject) {
            $('#room-topic').text(subject);
        }

        if (!notice) {
            var delay_css = delayed ? " delayed" : "";
            pmcxmpp.muc.addMessage(
                "<div class='message" + delay_css + "'>" +
                    "&lt;<span class='" + nick_class + "'>" +
                    nick + "</span>&gt; <span class='body'>" +
                    body + "</span></div>");
        } else {
            pmcxmpp.muc.addMessage("<div class='notice'>*** " + body +
                                "</div>");
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
    // Initialize
    pmcxmpp.muc.joined = false;
    pmcxmpp.muc.participants = {};
    // Presence
    pmcxmpp.connection.addHandler(pmcxmpp.muc.presenceReceived,
                                  null, "presence");
    pmcxmpp.connection.addHandler(pmcxmpp.muc.publicMessageReceived,
                                null, "message", "groupchat");

    // Room creation
    pmcxmpp.muc.nickname = Strophe.getNodeFromJid(pmcxmpp.jid);
    pmcxmpp.connection.send(
        $pres({
            to: pmcxmpp.muc.room+'/'+pmcxmpp.nickname
        }).c('x', {xmlns: pmcxmpp.muc.NS_MUC}));

});

$(document).bind('pmcxmpp.muc.roomJoined', function () {
    pmcxmpp.muc.joined = true;
    $('#room-name').text(pmcxmpp.muc.room);
    $('#participant-list').append('<li>' + pmcxmpp.muc.nickname + '</li>');
    pmcxmpp.muc.addMessage("<div class='notice'>*** Room joined.</div>");
});

$(document).bind('pmcxmpp.muc.userJoined', function (ev, nick) {
    $('#participant-list').append('<li>' + nick + '</li>');
    pmcxmpp.muc.addMessage("<div class='notice'>*** " + nick +
                           " joined.</div>");
});

$(document).bind('pmcxmpp.muc.userLeft', function (ev, nick) {
    $('#participant-list li').each(function () {
        if (nick === $(this).text()) {
            $(this).remove();
            return false;
        }
    });
    pmcxmpp.muc.addMessage("<div class='notice'>*** " + nick +
                           " left.</div>");
});

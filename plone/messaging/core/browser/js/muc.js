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
        if (room != pmcxmpp.muc.room) {
            var participating = false;
            for (var user in pmcxmpp.muc.participants) {
                var jid = pmcxmpp.muc.participants[user];
                if (from === jid) {
                    participating =true;
                    break
                }
            }
            if (!participating) {
                if ($(presence).attr('type') !== 'unavailable')
                    $(document).trigger('pmcxmpp.muc.userOnline', from);
                else 
                    $(document).trigger('pmcxmpp.muc.userOffline', from);
            }
            return true;
        }

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
            if ($(presence).find("status[code='210']").length > 0) {
                pmcxmpp.muc.nickname = Strophe.getResourceFromJid(from);
            }
            // room join complete
            $(document).trigger("pmcxmpp.muc.roomJoined");
            
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
        // look for room topic change
        var subject = $(message).children('subject').text();
        if (subject) {
            $('#room-topic').text(subject);
            return true;
        }

        if (room != pmcxmpp.muc.room) return true;

        var notice = !nick;

        var body = $(message).children('body').text();

        var delayed = $(message).children("delay").length > 0  ||
            $(message).children("x[xmlns='jabber:x:delay']").length > 0;


        pmcxmpp.muc.addMessage(body, nick, notice, delayed);
        return true;
    },

    addMessage: function (body, nick, notice, delayed) {
        var msg = "";
        if (!notice) {
            var delay_css = delayed ? " delayed" : "";
            // messages from ourself will be styled differently
            var nick_class = "nick";
            if (nick === pmcxmpp.muc.nickname) {
                nick_class += " self";
            }
            msg = "<div class='message" + delay_css + "'>" +
                  "&lt;<span class='" + nick_class + "'>" +
                                        nick + "</span>&gt;" +
                  " <span class='body'>" + body + "</span></div>"
        } else {
            msg = "<div class='notice'>*** " + body + "</div>"            
        }

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
    // Public messages
    pmcxmpp.connection.addHandler(pmcxmpp.muc.publicMessageReceived,
                                null, "message", "groupchat");

    pmcxmpp.connection.send($pres());
    // Room creation
    pmcxmpp.muc.nickname = Strophe.getNodeFromJid(pmcxmpp.jid);
    pmcxmpp.connection.send(
        $pres({
            to: pmcxmpp.muc.room+'/'+pmcxmpp.muc.nickname
        }).c('x', {xmlns: pmcxmpp.muc.NS_MUC}));

});

$(document).bind('pmcxmpp.muc.roomJoined', function () {
    pmcxmpp.muc.joined = true;
    $('#room-name').text(pmcxmpp.muc.room);
    $('#participant-list').append('<li>' + pmcxmpp.muc.nickname + '</li>');
    pmcxmpp.muc.addMessage("Room joined.", null, true, false);
});

$(document).bind('pmcxmpp.muc.userJoined', function (ev, nick) {
    $('#participant-list').append('<li>' + nick + '</li>');
    $('#online-list li').each(function () {
        if (nick === $(this).text()) {
            $(this).remove();
            return false;
        }
    });
    pmcxmpp.muc.addMessage(nick +" joined.", null, true, false);
});

$(document).bind('pmcxmpp.muc.userLeft', function (ev, nick) {
    $('#participant-list li').each(function () {
        if (nick === $(this).text()) {
            $(this).remove();
            return false;
        }
    });
    pmcxmpp.muc.addMessage(nick +" left.", null, true, false);
});

$(document).bind('pmcxmpp.muc.userOnline', function (ev, jid) {
    var nick = Strophe.getNodeFromJid(jid);
    $('#online-list').append('<li>' + nick + '</li>');
});

$(document).bind('pmcxmpp.muc.userOffline', function (ev, jid) {
    var nick = Strophe.getNodeFromJid(jid);
    $('#online-list li').each(function () {
        if (nick === $(this).text()) {
            $(this).remove();
            return false;
        }
    });
});

$(document).ready(function () {
    $('#input').keypress(function (ev) {
        if (ev.which === 13) {
            ev.preventDefault();

            var body = $(this).val();
            pmcxmpp.connection.send(
                $msg({
                    to: pmcxmpp.muc.room,
                    type: "groupchat"}).c('body').t(body));
            $(this).val('');
        }
    });
});

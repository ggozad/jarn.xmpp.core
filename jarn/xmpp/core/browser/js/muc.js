jarnxmpp.muc = {
    NS_MUC: "http://jabber.org/protocol/muc",
    NS_MUC_USER: "http://jabber.org/protocol/muc#user",
    room: null,
    nickname: null,
    joined: null,
    participants: null,
    online: null,

    presenceReceived: function (presence) {
        var from = $(presence).attr('from');
        var room = Strophe.getBareJidFromJid(from);

        // Is this for us?
        if (room != jarnxmpp.muc.room) {
            var participating = false;
            for (var user in jarnxmpp.muc.participants) {
                var jid = jarnxmpp.muc.participants[user];
                if (from === jid) {
                    participating =true;
                    break
                }
            }
            if (!participating) {
                var nick = Strophe.getNodeFromJid(from);
                if ($(presence).attr('type') !== 'unavailable') {
                    jarnxmpp.muc.online[nick] = from;
                    $(document).trigger('jarnxmpp.muc.userOnline', nick);
                }
                else {
                    delete jarnxmpp.muc.online[nick]
                    $(document).trigger('jarnxmpp.muc.userOffline', nick);
                }
            }
            return true;
        }

        var nick = Strophe.getResourceFromJid(from);

        if (!jarnxmpp.muc.participants[nick] &&
            $(presence).attr('type') !== 'unavailable') {

            // add to participant list
            var user_jid = $(presence).find('item').attr('jid');
            jarnxmpp.muc.participants[nick] = user_jid || true;

            if (jarnxmpp.muc.joined) {
                $(document).trigger('jarnxmpp.muc.userJoined', nick);
            }
        } else if (jarnxmpp.muc.participants[nick] &&
                   $(presence).attr('type') === 'unavailable') {
            delete jarnxmpp.muc.participants[nick];
            $(document).trigger('jarnxmpp.muc.userLeft', nick);
        }

        if ($(presence).attr('type') !== 'error' &&
                   !jarnxmpp.muc.joined) {
            if ($(presence).find("status[code='210']").length > 0) {
                jarnxmpp.muc.nickname = Strophe.getResourceFromJid(from);
            }
            // room join complete
            $(document).trigger("jarnxmpp.muc.roomJoined");
            
        } else if ($(presence).attr('type') === 'error' &&
                   !jarnxmpp.muc.joined) {
            // error joining room
            jarnxmpp.connection.disconnect();
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

        if (room != jarnxmpp.muc.room) return true;

        var notice = !nick;

        var body = $(message).children('body').text();

        var delayed = $(message).children("delay").length > 0  ||
            $(message).children("x[xmlns='jabber:x:delay']").length > 0;


        jarnxmpp.muc.addMessage(body, nick, notice, delayed);
        return true;
    },

    inviteToRoom: function(jid) {
        var invitation = $msg({to: jarnxmpp.muc.room})
            .c('x', {xmlns: jarnxmpp.muc.NS_MUC_USER})
            .c('invite', {to: Strophe.getBareJidFromJid(jid)});
        jarnxmpp.connection.send(invitation);
        jarnxmpp.muc.addMessage("Invitation sent.", null, true, false);
    },

    addMessage: function (body, nick, notice, delayed) {
        var msg = "";
        if (!notice) {
            var delay_css = delayed ? " delayed" : "";
            // messages from ourself will be styled differently
            var nick_class = "nick";
            if (nick === jarnxmpp.muc.nickname) {
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

$(document).bind('jarnxmpp.connected', function () {
    // Logging
    jarnxmpp.connection.rawInput = jarnxmpp.rawInput;
    jarnxmpp.connection.rawOutput = jarnxmpp.rawOutput;
    // Initialize
    jarnxmpp.muc.joined = false;
    jarnxmpp.muc.participants = {};
    jarnxmpp.muc.online = {};
    // Presence
    jarnxmpp.connection.addHandler(jarnxmpp.muc.presenceReceived,
                                  null, "presence");
    // Public messages
    jarnxmpp.connection.addHandler(jarnxmpp.muc.publicMessageReceived,
                                null, "message", "groupchat");

    // Room creation
    jarnxmpp.connection.send($pres());
    jarnxmpp.muc.nickname = Strophe.getNodeFromJid(jarnxmpp.jid);
    jarnxmpp.connection.send(
        $pres({
            to: jarnxmpp.muc.room+'/'+jarnxmpp.muc.nickname
        }).c('x', {xmlns: jarnxmpp.muc.NS_MUC}));

});

$(document).bind('jarnxmpp.muc.roomJoined', function () {
    jarnxmpp.muc.joined = true;
    $('#room-name').text(jarnxmpp.muc.room);
    $('#participant-list').append('<li>' + jarnxmpp.muc.nickname + '</li>');
    jarnxmpp.muc.addMessage("Room joined.", null, true, false);
});

$(document).bind('jarnxmpp.muc.userJoined', function (ev, nick) {
    $('#participant-list').append('<li>' + nick + '</li>');
    $('#online-list li').each(function () {
        if (nick === $(this).text()) {
            $(this).remove();
            return false;
        }
    });
    jarnxmpp.muc.addMessage(nick +" joined.", null, true, false);
});

$(document).bind('jarnxmpp.muc.userLeft', function (ev, nick) {
    $('#participant-list li').each(function () {
        if (nick === $(this).text()) {
            $(this).remove();
            return false;
        }
    });
    jarnxmpp.muc.addMessage(nick +" left.", null, true, false);
});

$(document).bind('jarnxmpp.muc.userOnline', function (ev, nick) {
    if (!(nick in jarnxmpp.muc.participants)) {
        $('#online-list').append('<li>' +
                                 '<span>' + nick + '</span>' +
                                 '<button class="invite"></button>' +
                                 '</li>');
    }
});

$(document).bind('jarnxmpp.muc.userOffline', function (ev, nick) {
    $('#online-list li').each(function () {
        if (nick === $(this).find('span').text()) {
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
            jarnxmpp.connection.send(
                $msg({
                    to: jarnxmpp.muc.room,
                    type: "groupchat"}).c('body').t(body));
            $(this).val('');
        }
    });

    $('.invite').live('click', function () {
        var nick = $(this).parent().find('span').text();
        var jid = jarnxmpp.muc.online[nick];
        jarnxmpp.muc.inviteToRoom(jid);
    });
});

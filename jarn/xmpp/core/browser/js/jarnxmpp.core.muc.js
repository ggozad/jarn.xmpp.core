jarnxmpp.muc = {
    NS_MUC: "http://jabber.org/protocol/muc",
    NS_MUC_USER: "http://jabber.org/protocol/muc#user",
    room: null,
    nickname: null,
    joined: false,
    participants: {},

    leaveRoom: function() {
        $(document).unbind('jarnxmpp.presence', jarnxmpp.muc.presenceReceived);
        jarnxmpp.connection.send($pres({
            to: jarnxmpp.muc.room,
            'type': 'unavailable'}));
        jarnxmpp.muc.joined = false;
        jarnxmpp.muc.nickname = null;
        jarnxmpp.muc.room = null;
        jarnxmpp.muc.participants = {};
    },

    joinRoom: function (room) {
        jarnxmpp.muc.room=room; 
        jarnxmpp.muc.nickname = Strophe.getNodeFromJid(jarnxmpp.jid);

        for (var user in jarnxmpp.Presence.online) {
            if (jarnxmpp.Presence.online.hasOwnProperty(user) && user!==Strophe.getNodeFromJid(jarnxmpp.connection.jid)) {
                $(document).trigger('jarnxmpp.muc.userOnline', user);
            }
        }
        // Public messages
        jarnxmpp.connection.addHandler(jarnxmpp.muc.publicMessageReceived,
                                    null, "message", "groupchat");

        $('#chat-container').parents('.overlay').bind('onClose', jarnxmpp.muc.leaveRoom);
        $('#muc-input').bind('keypress', function (ev) {
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
            if (jarnxmpp.Presence.online[nick].length > 0)
                jarnxmpp.muc.inviteToRoom(jarnxmpp.Presence.online[nick][0]);
        });

        $(document).bind('jarnxmpp.presence', jarnxmpp.muc.presenceReceived);
        jarnxmpp.connection.send(
            $pres({
                to: jarnxmpp.muc.room+'/'+jarnxmpp.muc.nickname
            }).c('x', {xmlns: jarnxmpp.muc.NS_MUC}));
    },

    presenceReceived: function (event, jid, status, presence) {
        var bare_jid = Strophe.getBareJidFromJid(jid);
        // Is this for us?
        if (bare_jid != jarnxmpp.muc.room) {
            var userid = Strophe.getNodeFromJid(bare_jid);
            if (userid in jarnxmpp.muc.participants)
                return;
            if (status === 'online')
                $(document).trigger('jarnxmpp.muc.userOnline', userid);
            else if (!(userid in jarnxmpp.Presence.online))
                $(document).trigger('jarnxmpp.muc.userOffline', userid);
            return true;
        }

        var nick = Strophe.getResourceFromJid(jid);

        if (!jarnxmpp.muc.participants[nick] &&
            $(presence).attr('type') !== 'unavailable') {
            // add to participant list
            jarnxmpp.muc.participants[nick] = jid || true;
            if (jarnxmpp.muc.joined) 
                $(document).trigger('jarnxmpp.muc.userJoined', nick);

        } else if (jarnxmpp.muc.participants[nick] && $(presence).attr('type') === 'unavailable') {
            delete jarnxmpp.muc.participants[nick];
            $(document).trigger('jarnxmpp.muc.userLeft', nick);
        }

        if ($(presence).attr('type') !== 'error' && !jarnxmpp.muc.joined) {
            if ($(presence).find("status[code='210']").length > 0)
                jarnxmpp.muc.nickname = nick;
            // room join complete
            $(document).trigger("jarnxmpp.muc.roomJoined", [nick]);
            
        } else if ($(presence).attr('type') === 'error' && !jarnxmpp.muc.joined) {
            // error joining room
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

        var body = $(message).children('body').text();
        var delayed = $(message).children("delay").length > 0  ||
            $(message).children("x[xmlns='jabber:x:delay']").length > 0;

        var event = jQuery.Event('jarnxmpp.muc.displayPublicMessage');
        event.body = body;
        event.nick = nick;
        event.notice = !nick;
        event.delayed = delayed;
        $(document).trigger(event);
        return true;
    },

    inviteToRoom: function(jid) {
        var invitation = $msg({to: jarnxmpp.muc.room})
            .c('x', {xmlns: jarnxmpp.muc.NS_MUC_USER})
            .c('invite', {to: Strophe.getBareJidFromJid(jid)});
        jarnxmpp.connection.send(invitation);
        var event = jQuery.Event('jarnxmpp.muc.displayPublicMessage');
        event.body = "Invitation sent.";
        event.notice = true;
        $(document).trigger(event);
    },

};

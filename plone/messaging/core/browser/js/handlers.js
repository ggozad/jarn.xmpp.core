pmcxmpp.Messages = {
    messageReceived: function (message) {
        var body = $(message).children('body').text();
        if (body=="") {
            return true; // This is a typing notification, we do not handle it here...
        }
        var xhtml_body = $(message).find('html > body').contents();
        event = jQuery.Event('pmcxmpp.message');
        if (xhtml_body.length>0) {
            event.mtype = 'xhtml';
            event.body = xhtml_body.html();
        } else {
            event.body = body;
            event.mtype = 'text'
        }
        event.from = $(message).attr('from');
        $(document).trigger(event);
        return true;
    },

    invitationReceived: function(message) {
        room = $(message).attr('from');
        from = $(message).find('invite').attr('from');
        event = jQuery.Event('pmcxmpp.roomInvitation');
        event.room = room;
        event.from = from;
        $(document).trigger(event);
        return true;
    }
};

pmcxmpp.Roster = {
    rosterSet: function(iq) {
        // XXX: Fill me in
        return true;
    },
    rosterResult: function(iq) {
        // XXX: Fill me in
        return true;
    },

    rosterSuggestedItem: function(msg) {
        $(msg).find('item').each(function () {
            var jid = $(this).attr('jid');
            var action = $(this).attr('action');
            if (action === 'add') {
                pmcxmpp.connection.send($pres({
                    to: jid,
                    "type": "subscribe"}));
            }
        });
    }
};

pmcxmpp.Presence = {
    presenceReceived: function (presence) {
        var ptype = $(presence).attr('type');
        var from = $(presence).attr('from');
        var status = '';
        //
        // User wants to subscribe to us. Always approve and
        // ask to subscribe to him
        //
        if (ptype === 'subscribe' ) {
            pmcxmpp.connection.send($pres({
                to: from,
                "type": "subscribed"}));
            pmcxmpp.connection.send($pres({
                to: from,
                "type": "subscribe"}));
        }
        //
        // Presence has changed
        //
        else if (ptype !== 'error') {
            if (ptype === 'unavailable') {
                status = 'offline';
            } else {
                var show = $(presence).find('show').text(); 
                if (show === '' || show === '') {
                    status = 'online'
                } else {
                    status = 'away'
                }
            }
            $(document).trigger('pmcxmpp.presence', [from, status]);
        }
        return true;
    }
};

pmcxmpp.PubSub = {
    eventReceived: function(msg) {
        var items = $(msg).find('item');
        if (items.length>0) {
            for (var i = 0; i < items.length; i++) {
                var entry = $(items[i]).children('entry')
                var event = jQuery.Event('pmcxmpp.nodePublished');
                event.author = $(entry).children('author').text();
                event.published = $(entry).children('published').text();
                event.content = $(entry).children('content').text();
                $(document).trigger(event);
            }
        }
        return true;
    }
};

$(document).bind('pmcxmpp.connected', function () {
    // Logging
    pmcxmpp.connection.rawInput = pmcxmpp.rawInput;
    pmcxmpp.connection.rawOutput = pmcxmpp.rawOutput;
    // Messages
    pmcxmpp.connection.addHandler(pmcxmpp.Messages.messageReceived, null, 'message', 'chat');
    pmcxmpp.connection.addHandler(pmcxmpp.Messages.invitationReceived, 'http://jabber.org/protocol/muc#user', 'message', null);
    //Roster
    pmcxmpp.connection.addHandler(pmcxmpp.Roster.rosterSet, Strophe.NS.ROSTER, 'iq', 'set');
    pmcxmpp.connection.addHandler(pmcxmpp.Roster.rosterResult, Strophe.NS.ROSTER, 'iq', 'result');
    // Presence
    pmcxmpp.connection.addHandler(pmcxmpp.Presence.presenceReceived, null, 'presence', null);
    // PubSub
    pmcxmpp.connection.addHandler(pmcxmpp.PubSub.eventReceived, null, 'message', null, null, pmcxmpp.pubsub_jid);
    pmcxmpp.connection.addHandler(pmcxmpp.Roster.rosterSuggestedItem, 'http://jabber.org/protocol/rosterx', 'message', null);
    pmcxmpp.connection.send($pres());
});

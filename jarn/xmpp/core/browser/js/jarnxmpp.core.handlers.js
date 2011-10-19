jarnxmpp = {};

jarnxmpp.Storage = {

    storage: null,
    init: function () {
        try {
            if ('sessionStorage' in window &&
                window.sessionStorage !== null &&
                'JSON' in window &&
                window.JSON !== null) {
                    jarnxmpp.Storage.storage = sessionStorage;
                    if (!('_user_info' in jarnxmpp.Storage.storage))
                        jarnxmpp.Storage.set('_user_info', {});
                }
        } catch(e) {}

    },

    get: function (key) {
        if (key in sessionStorage) {
            return JSON.parse(sessionStorage[key]);
        }
        return null;
    },

    set: function (key, value) {
        sessionStorage[key] = JSON.stringify(value);
    }

};

jarnxmpp.Storage.init();

jarnxmpp.Messages = {
    messageReceived: function (message) {
        var body = $(message).children('body').text();
        if (body==="") {
            return true; // This is a typing notification, we do not handle it here...
        }
        var xhtml_body = $(message).find('html > body').contents(),
            event = jQuery.Event('jarnxmpp.message');
        event.from = $(message).attr('from');
        if (xhtml_body.length>0) {
            event.mtype = 'xhtml';
            event.body = xhtml_body.html();
        } else {
            event.body = body;
            event.mtype = 'text';
        }
        $(document).trigger(event);
        return true;
    },
};

jarnxmpp.Roster = {

    rosterSuggestedItem: function(msg) {
        $(msg).find('item').each(function () {
            var jid = $(this).attr('jid');
            var action = $(this).attr('action');
            if (action === 'add') {
                jarnxmpp.connection.send($pres({
                    to: jid,
                    "type": "subscribe"}));
            }
        });
        return true;
    }
};

jarnxmpp.Presence = {
    online: {},
    _user_info: {},

    onlineCount: function () {
        var counter = 0;
        for (var user in jarnxmpp.Presence.online) {
            if (jarnxmpp.Presence.online.hasOwnProperty(user)) {
                counter += 1;
            }
        }
        return counter;
    },

    presenceReceived: function (presence) {
        var ptype = $(presence).attr('type'),
            from = $(presence).attr('from'),
            user_id = Strophe.getNodeFromJid(from),
            status = '';
        // User wants to subscribe to us. Always approve and
        // ask to subscribe to him
        if (ptype === 'subscribe' ) {
            jarnxmpp.connection.send($pres({
                to: from,
                "type": "subscribed"}));
            jarnxmpp.connection.send($pres({
                to: from,
                "type": "subscribe"}));
        }
        // Presence has changed
        else if (ptype !== 'error') {
            if (ptype === 'unavailable') {
                status = 'offline';
            } else {
                status = ($(presence).find('show').text() === '') ? 'online' : 'away';
            }
            if (status !== 'offline') {
                if (jarnxmpp.Presence.online.hasOwnProperty(user_id))
                    jarnxmpp.Presence.online[user_id].push(from);
                else
                    jarnxmpp.Presence.online[user_id] = [from];
            } else {
                if (jarnxmpp.Presence.online.hasOwnProperty(user_id)) {
                    var pos = jarnxmpp.Presence.online[user_id].indexOf(from);
                    if (pos >= 0) {
                        jarnxmpp.Presence.online[user_id].splice(pos, 1);
                    }
                    if (jarnxmpp.Presence.online[user_id].length === 0)
                        delete jarnxmpp.Presence.online[user_id];
                }
            }
            $(document).trigger('jarnxmpp.presence', [from, status, presence]);
        }
        return true;
    },

    getUserInfo: function(user_id, callback) {
        // User info on browsers without storage
        if (jarnxmpp.Storage.storage === null) {
            if (user_id in jarnxmpp.Presence._user_info) {
                callback(jarnxmpp.Presence._user_info[user_id]);
            } else {
                $.getJSON(portal_url+"/xmpp-userinfo?user_id="+user_id, function(data) {
                    jarnxmpp.Presence._user_info[user_id] = data;
                    callback(data);
                });
            }
        } else {
            _user_info = jarnxmpp.Storage.get('_user_info');
            if (user_id in _user_info) {
                callback(_user_info[user_id]);
            } else {
                $.getJSON(portal_url+"/xmpp-userinfo?user_id="+user_id, function(data) {
                    _user_info[user_id] = data;
                    jarnxmpp.Storage.set('_user_info', _user_info);
                    callback(data);
                });
            }
        }
    }
};

jarnxmpp.PubSub = {

    _ISODateString: function(d) {
        function pad(n){
            return n<10 ? '0'+n : n;
        }
        return d.getUTCFullYear() + '-' +
            pad(d.getUTCMonth() + 1) + '-' +
            pad(d.getUTCDate()) + 'T' +
            pad(d.getUTCHours()) + ':' +
            pad(d.getUTCMinutes()) + ':' +
            pad(d.getUTCSeconds()) + 'Z';
    },

    eventReceived: function(msg) {
        $.each($('event > items', msg), function (idx, node_items) {
            var node = $(node_items).attr('node');
            $.each($('>item', node_items), function(iidx, item) {
                var item_id = $(item).attr('id');
                var entry = $('entry[xmlns="http://www.w3.org/2005/Atom"]:first', item);
                if (entry.length > 0) {
                    var event = jQuery.Event('jarnxmpp.pubsubEntryPublished');
                    event.node = node;
                    event.id = item_id;
                    event.content = $('content', entry).text();
                    event.author = $('author', entry).text();
                    event.published = $('published', entry).text();
                    event.updated = $('updated', entry).text();
                    $('geolocation:first', entry).each(function (idx, geoel) {
                        var coords = {
                            latitude: $(geoel).attr('latitude'),
                            longitude: $(geoel).attr('longitude')
                        };
                        event.geolocation = coords;
                    });
                    $(document).trigger(event);
                }
            });
        });
        return true;
    },

    publishToPersonalNode: function(node, text, share_location, callback) {
        if (text === '' || node === '') return;
        $.getJSON(portal_url+'/content-transform?', {text: text}, function(data) {
            var pubid = jarnxmpp.connection.getUniqueId("publishnode"),
                publish_elem = Strophe.xmlElement("publish", [["node",node],["jid",jarnxmpp.jid]]),
                item = Strophe.xmlElement("item",[]),
                entry = Strophe.xmlElement('entry', [['xmlns', 'http://www.w3.org/2005/Atom']]),
                author = Strophe.xmlElement('author', [], Strophe.getNodeFromJid(jarnxmpp.jid)),
                now = jarnxmpp.PubSub._ISODateString(new Date()),
                updated = Strophe.xmlElement('updated', [], now),
                published = Strophe.xmlElement('published', [], now),
                content = Strophe.xmlElement('content', [], data.text);
            entry.appendChild(author);
            entry.appendChild(updated);
            entry.appendChild(published);
            entry.appendChild(content);
            if (share_location && jarnxmpp.geolocation!==null) {
                var coords = jarnxmpp.geolocation.coords;
                //entry.appendChild(Strophe.xmlElement('longitude', [], coords.longitude));
                //entry.appendChild(Strophe.xmlElement('latitude', [], coords.latitude));
                entry.appendChild(Strophe.xmlElement(
                    'geolocation',
                    [['latitude', coords.latitude],
                     ['longitude', coords.longitude]]));
            }
            item.appendChild(entry);
            publish_elem.appendChild(item);
            var pub = $iq({from:jarnxmpp.jid, to:jarnxmpp.pubsub_jid, type:'set', id:pubid});
            pub.c('pubsub', { xmlns:Strophe.NS.PUBSUB }).cnode(publish_elem);
            if (typeof(callback) !== 'undefined')
                jarnxmpp.connection.addHandler(callback, null, 'iq', null, pubid, null);
            jarnxmpp.connection.send(pub);
        });

    },
};

jarnxmpp.onConnect = function (status) {
    if ((status === Strophe.Status.ATTACHED) ||
        (status === Strophe.Status.CONNECTED)) {
        $(window).bind('beforeunload', function() {
            $(document).trigger('jarnxmpp.disconnecting');
            var presence = $pres({type: 'unavailable'});
            jarnxmpp.connection.sync = true;
            jarnxmpp.connection.send(presence);
            jarnxmpp.connection.disconnect();
            jarnxmpp.connection.flush();
        });
        $(document).trigger('jarnxmpp.connected');
    } else if (status === Strophe.Status.DISCONNECTED) {
        $(document).trigger('jarnxmpp.disconnected');
    }
};

jarnxmpp.rawInput = function(data) {
    var event = jQuery.Event('jarnxmpp.dataReceived');
    event.text = data;
    $(document).trigger(event);
};

jarnxmpp.rawOutput = function (data) {
    var event = jQuery.Event('jarnxmpp.dataSent');
    event.text = data;
    $(document).trigger(event);
};

$(document).bind('jarnxmpp.connected', function () {
    // Logging
    jarnxmpp.connection.rawInput = jarnxmpp.rawInput;
    jarnxmpp.connection.rawOutput = jarnxmpp.rawOutput;
    // Messages
    jarnxmpp.connection.addHandler(jarnxmpp.Messages.messageReceived, null, 'message', 'chat');
    //Roster
    jarnxmpp.connection.addHandler(jarnxmpp.Roster.rosterResult, Strophe.NS.ROSTER, 'iq', 'result');
    // Presence
    jarnxmpp.connection.addHandler(jarnxmpp.Presence.presenceReceived, null, 'presence', null);
    // PubSub
    jarnxmpp.connection.addHandler(jarnxmpp.PubSub.eventReceived, null, 'message', null, null, jarnxmpp.pubsub_jid);
    jarnxmpp.connection.addHandler(jarnxmpp.Roster.rosterSuggestedItem, 'http://jabber.org/protocol/rosterx', 'message', null);
    jarnxmpp.connection.send($pres());
});

$(document).bind('jarnxmpp.disconnecting', function () {
    if (jarnxmpp.Storage.storage !== null)
        jarnxmpp.Storage.set('online-count', jarnxmpp.Presence.onlineCount());
});

$(document).ready(function () {

    $.getJSON(portal_url + '/@@xmpp-loader', function (data) {
        jarnxmpp.BOSH_SERVICE = data.BOSH_SERVICE;
        jarnxmpp.pubsub_jid = data.pubsub_jid;
        jarnxmpp.jid = data.jid;
        jarnxmpp.connection = new Strophe.Connection(jarnxmpp.BOSH_SERVICE);
        if (('rid' in data) && ('sid' in data))
            jarnxmpp.connection.attach(jarnxmpp.jid, data.sid, data.rid, jarnxmpp.onConnect);
        else
            jarnxmpp.connection.connect(jarnxmpp.jid, data.password, jarnxmpp.onConnect);
    });
    jarnxmpp.geolocation = null;
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(geolocation) {
                jarnxmpp.geolocation = geolocation;
                $(document).trigger('jarnxmpp.haveGeolocation');
            }, function(error) {}, {maximumAge:600000});
    }
});

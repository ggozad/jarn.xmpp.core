/*global $:false, document:false, window:false, portal_url:false,
$msg:false, Strophe:false, setTimeout:false, navigator:false, jarn:false, google:false, jarnxmpp:false, jQuery:false, sessionStorage:false, $iq:false, $pres:false, Image:false, */

(function (jarnxmpp, $) {

    jarnxmpp.Storage = {

        storage: null,
        init: function () {
            try {
                if ('sessionStorage' in window && window.sessionStorage !== null && JSON in window && window.JSON !== null) {
                    jarnxmpp.Storage.storage = sessionStorage;
                    if (!('_user_info' in jarnxmpp.Storage.storage)) {
                        jarnxmpp.Storage.set('_user_info', {});
                    }
                    if (!('_vCards' in jarnxmpp.Storage.storage)) {
                        jarnxmpp.Storage.set('_vCards', {});
                    }
                    if (!('_subscriptions' in jarnxmpp.Storage.storage)) {
                        jarnxmpp.Storage.set('_subscriptions', null);
                    }
                }
            } catch (e) {}
        },

        get: function (key) {
            if (key in sessionStorage) {
                return JSON.parse(sessionStorage[key]);
            }
            return null;
        },

        set: function (key, value) {
            sessionStorage[key] = JSON.stringify(value);
        },

        xmppGet: function (key, callback) {
            var stanza = $iq({type: 'get'})
                .c('query', {xmlns: 'jabber:iq:private'})
                .c('jarnxmpp', {xmlns: 'http://jarn.com/ns/jarnxmpp:prefs:' + key})
                .tree();
            jarnxmpp.connection.sendIQ(stanza, function success(result) {
                callback($('jarnxmpp ' + 'value', result).first().text());
            });
        },

        xmppSet: function (key, value) {
            var stanza = $iq({type: 'set'})
                .c('query', {xmlns: 'jabber:iq:private'})
                .c('jarnxmpp', {xmlns: 'http://jarn.com/ns/jarnxmpp:prefs:' + key})
                .c('value', value)
                .tree();
            jarnxmpp.connection.sendIQ(stanza);
        }
    };

    jarnxmpp.Storage.init();

    jarnxmpp.Messages = {
        messageReceived: function (message) {
            var body = $(message).children('body').text();
            if (body === "") {
                return true; // This is a typing notification, we do not handle it here...
            }
            var xhtml_body = $(message).find('html > body').contents(),
                event = jQuery.Event('jarnxmpp.message');
            event.from = $(message).attr('from');
            if (xhtml_body.length > 0) {
                event.mtype = 'xhtml';
                event.body = xhtml_body.html();
            } else {
                event.body = body;
                event.mtype = 'text';
            }
            $(document).trigger(event);
            return true;
        }
    };

    jarnxmpp.Roster = {

        rosterSuggestedItem: function (msg) {
            $(msg).find('item').each(function () {
                var jid = $(this).attr('jid');
                var action = $(this).attr('action');
                if (action === 'add') {
                    jarnxmpp.connection.send($pres({to: jid, type: 'subscribe'}));
                }
            });
            return true;
        }
    };

    jarnxmpp.Presence = {
        online: {},
        _user_info: {},

        onlineCount: function () {
            var me = Strophe.getNodeFromJid(jarnxmpp.connection.jid),
                counter = 0,
                user;
            for (user in jarnxmpp.Presence.online) {
                if ((jarnxmpp.Presence.online.hasOwnProperty(user)) && user !== me) {
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
            if (ptype === 'subscribe') {
                jarnxmpp.connection.send($pres({to: from, type: 'subscribed'}));
                jarnxmpp.connection.send($pres({to: from, type: 'subscribe'}));
            } else if (ptype !== 'error') { // Presence has changed
                if (ptype === 'unavailable') {
                    status = 'offline';
                } else {
                    status = ($(presence).find('show').text() === '') ? 'online' : 'away';
                }
                if (status !== 'offline') {
                    if (jarnxmpp.Presence.online.hasOwnProperty(user_id)) {
                        jarnxmpp.Presence.online[user_id].push(from);
                    } else {
                        jarnxmpp.Presence.online[user_id] = [from];
                    }
                } else {
                    if (jarnxmpp.Presence.online.hasOwnProperty(user_id)) {
                        var pos = jarnxmpp.Presence.online[user_id].indexOf(from);
                        if (pos >= 0) {
                            jarnxmpp.Presence.online[user_id].splice(pos, 1);
                        }
                        if (jarnxmpp.Presence.online[user_id].length === 0) {
                            delete jarnxmpp.Presence.online[user_id];
                        }
                    }
                }
                $(document).trigger('jarnxmpp.presence', [from, status, presence]);
            }
            return true;
        },

        getUserInfo: function (user_id, callback) {
            // User info on browsers without storage
            if (jarnxmpp.Storage.storage === null) {
                if (user_id in jarnxmpp.Presence._user_info) {
                    callback(jarnxmpp.Presence._user_info[user_id]);
                } else {
                    $.getJSON(portal_url + "/xmpp-userinfo?user_id=" + user_id, function (data) {
                        jarnxmpp.Presence._user_info[user_id] = data;
                        callback(data);
                    });
                }
            } else {
                var _user_info = jarnxmpp.Storage.get('_user_info');
                if (user_id in _user_info) {
                    callback(_user_info[user_id]);
                } else {
                    $.getJSON(portal_url + "/xmpp-userinfo?user_id=" + user_id, function (data) {
                        _user_info[user_id] = data;
                        jarnxmpp.Storage.set('_user_info', _user_info);
                        callback(data);
                    });
                }
            }
        }
    };

    jarnxmpp.vCard = {

        _vCards: {},

        _getVCard: function (jid, callback) {
            var stanza =
                $iq({type: 'get', to: jid})
                .c('vCard', {xmlns: 'vcard-temp'}).tree();
            jarnxmpp.connection.sendIQ(stanza, function (data) {
                var result = {};
                $('vCard[xmlns="vcard-temp"]', data).children().each(function (idx, element) {
                    result[element.nodeName] = element.textContent;
                });
                if (typeof (callback) !== 'undefined') {
                    callback(result);
                }
            });
        },

        getVCard: function (jid, callback) {
            jid = Strophe.getBareJidFromJid(jid);
            if (jarnxmpp.Storage.storage === null) {
                if (jid in jarnxmpp.vCard._vCards) {
                    callback(jarnxmpp.vCard._vCards[jid]);
                } else {
                    jarnxmpp.vCard._getVCard(jid, function (result) {
                        jarnxmpp.vCard._vCards[jid] = result;
                        callback(result);
                    });
                }
            } else {
                var _vCards = jarnxmpp.Storage.get('_vCards');
                if (jid in _vCards) {
                    callback(_vCards[jid]);
                } else {
                    jarnxmpp.vCard._getVCard(jid, function (result) {
                        _vCards[jid] = result;
                        jarnxmpp.Storage.set('_vCards', _vCards);
                        callback(result);
                    });
                }
            }
        },

        setVCard: function (params, photoUrl) {
            var key,
                vCard = Strophe.xmlElement('vCard', [['xmlns', 'vcard-temp'], ['version', '2.0']]);
            for (key in params) {
                if (params.hasOwnProperty(key)) {
                    vCard.appendChild(Strophe.xmlElement(key, [], params[key]));
                }
            }
            var send = function () {
                var stanza = $iq({type: 'set'}).cnode(vCard).tree();
                jarnxmpp.connection.sendIQ(stanza);
            };
            if (typeof (photoUrl) === 'undefined') {
                send();
            } else {
                jarnxmpp.vCard.getBase64Image(photoUrl, function (base64img) {
                    base64img = base64img.replace(/^data:image\/png;base64,/, "");
                    var photo = Strophe.xmlElement('PHOTO');
                    photo.appendChild(Strophe.xmlElement('TYPE', [], 'image/png'));
                    photo.appendChild(Strophe.xmlElement('BINVAL', [], base64img));
                    vCard.appendChild(photo);
                    send();
                });
            }
        },

        getBase64Image: function (url, callback) {
            // Create the element, then draw it on a canvas to get the base64 data.
            var img = new Image();
            $(img).load(function () {
                var canvas = document.createElement('canvas');
                canvas.width = img.width;
                canvas.height = img.height;
                var ctx = canvas.getContext("2d");
                ctx.drawImage(img, 0, 0);
                callback(canvas.toDataURL('image/png'));
            }).attr('src', url);
        }
    };

    jarnxmpp.PubSub = {

        _ISODateString: function (d) {
            function pad(n) {
                return n < 10 ? '0' + n : n;
            }
            return d.getUTCFullYear() + '-' +
                pad(d.getUTCMonth() + 1) + '-' +
                pad(d.getUTCDate()) + 'T' +
                pad(d.getUTCHours()) + ':' +
                pad(d.getUTCMinutes()) + ':' +
                pad(d.getUTCSeconds()) + 'Z';
        },

        eventReceived: function (msg) {
            $.each($('event > items', msg), function (idx, node_items) {
                var node = $(node_items).attr('node');
                $.each($('>item', node_items), function (iidx, item) {
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
                        event.pnode = $('parent', entry).text();
                        $(document).trigger(event);
                    }
                });
            });
            return true;
        },

        publish: function (node, pnode, text, location, callback) {
            if (text === '' || node === '') {
                return;
            }
            $.getJSON(portal_url + '/content-transform?', {text: text}, function (data) {
                var publish_elem = Strophe.xmlElement("publish", [["node", node], ["jid", jarnxmpp.jid]]),
                    item = Strophe.xmlElement("item", []),
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
                if (location !== null && navigator.geolocation) {
                    var coords = location.coords;
                    entry.appendChild(Strophe.xmlElement(
                        'geolocation',
                        [['latitude', coords.latitude], ['longitude', coords.longitude]]
                    ));
                }
                if (pnode) {
                    entry.appendChild(Strophe.xmlElement('parent', [], pnode));
                }
                item.appendChild(entry);
                publish_elem.appendChild(item);
                var stanza = $iq({from: jarnxmpp.jid, to: jarnxmpp.pubsub_jid, type: 'set'})
                    .c('pubsub', {xmlns: Strophe.NS.PUBSUB }).cnode(publish_elem);
                jarnxmpp.connection.sendIQ(stanza.tree(), function (result) {
                    if (typeof (callback) !== 'undefined') {
                        callback(result);
                    }
                });
            });

        },

        discoItems: function (node, callback) {
            var stanza = $iq({type: 'get', to: jarnxmpp.pubsub_jid})
                .c('query', {xmlns: Strophe.NS.DISCO_ITEMS, node: node});
            jarnxmpp.connection.sendIQ(stanza.tree(), function (result) {
                callback($('item', result));
            });
        },

        items: function (node, callback) {
            var stanza = $iq({type: 'get', to: jarnxmpp.pubsub_jid})
                .c('pubsub', {xmlns: Strophe.NS.PUBSUB, node: node})
                .c('items', {node: node});
            jarnxmpp.connection.sendIQ(stanza.tree(), function (result) {
                callback($('item', result));
            });
        },

        getNodes: function (node, callback) {
            var stanza = $iq({type: 'get', to: jarnxmpp.pubsub_jid});
            if (node) {
                stanza.c('query', {xmlns: Strophe.NS.DISCO_ITEMS, node: node});
            } else {
                stanza.c('query', {xmlns: Strophe.NS.DISCO_ITEMS});
            }
            jarnxmpp.connection.sendIQ(stanza.tree(), function (result) {
                var nodes = $.map($('item', result), function (item) { return $(item).attr('node'); });
                callback(nodes);
            });
        },

        subscribe: function (node, callback) {
            var stanza = $iq({type: 'set', to: jarnxmpp.pubsub_jid})
                .c('pubsub', {xmlns: Strophe.NS.PUBSUB})
                .c('subscribe', {node: node, jid: Strophe.getBareJidFromJid(jarnxmpp.connection.jid) });
            jarnxmpp.connection.sendIQ(stanza.tree(), function (result) {
                if (jarnxmpp.Storage.storage !== null) {
                    jarnxmpp.PubSub.getSubscriptions(function (subscriptions) {
                        subscriptions.push(node);
                        jarnxmpp.Storage.set('_subscriptions', subscriptions);
                    });
                }
                callback(true);
            }, function (error) {
                callback(false);
            });
        },

        unsubscribe: function (node, subid, callback) {
            var stanza = $iq({type: 'set', to: jarnxmpp.pubsub_jid})
                .c('pubsub', {xmlns: Strophe.NS.PUBSUB});
            if (subid) {
                stanza.c('unsubscribe', {node: node, subid: subid, jid: Strophe.getBareJidFromJid(jarnxmpp.connection.jid) });
            } else {
                stanza.c('unsubscribe', {node: node, jid: Strophe.getBareJidFromJid(jarnxmpp.connection.jid) });
            }
            jarnxmpp.connection.sendIQ(stanza.tree(),
                function (result) {
                    if (jarnxmpp.Storage.storage !== null) {
                        jarnxmpp.PubSub.getSubscriptions(function (subscriptions) {
                            var idx = subscriptions.indexOf(node);
                            subscriptions.splice(idx, 1);
                            jarnxmpp.Storage.set('_subscriptions', subscriptions);
                        });
                    }
                    callback(true);
                },
                function (error) {
                    callback(false);
                });
        },

        getSubscriptions: function (callback) {
            if (jarnxmpp.Storage.storage !== null) {
                var subscriptions = jarnxmpp.Storage.get('_subscriptions');
                if (subscriptions) {
                    callback(subscriptions);
                    return;
                }
            }
            var stanza = $iq({type: 'get', to: jarnxmpp.pubsub_jid})
                .c('pubsub', {xmlns: Strophe.NS.PUBSUB})
                .c('subscriptions').tree();
            jarnxmpp.connection.sendIQ(stanza, function (result) {
                var subscriptions = $.map($('subscription', result), function (item) { return $(item).attr('node'); });
                if (jarnxmpp.Storage.storage !== null) {
                    jarnxmpp.Storage.set('_subscriptions', subscriptions);
                }
                callback(subscriptions);
            });
        }
    };

    jarnxmpp.onConnect = function (status) {
        if ((status === Strophe.Status.ATTACHED) || (status === Strophe.Status.CONNECTED)) {
            $(window).bind('beforeunload', function () {
                $(document).trigger('jarnxmpp.disconnecting');
                var presence = $pres({type: 'unavailable'});
                jarnxmpp.connection.send(presence);
                jarnxmpp.connection.disconnect();
                jarnxmpp.connection.flush();
            });
            $(document).trigger('jarnxmpp.connected');
        } else if (status === Strophe.Status.DISCONNECTED) {
            $(document).trigger('jarnxmpp.disconnected');
        }
    };

    jarnxmpp.rawInput = function (data) {
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
        Strophe.addNamespace('PUBSUB', 'http://jabber.org/protocol/pubsub');
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
        if (jarnxmpp.Storage.storage !== null) {
            jarnxmpp.Storage.set('online-count', jarnxmpp.Presence.onlineCount());
        }
    });

    $(document).ready(function () {

        $.getJSON(portal_url + '/@@xmpp-loader', function (data) {
            if (!(('rid' in data) && ('sid' in data) && ('BOSH_SERVICE' in data))) {
                return;
            }
            jarnxmpp.BOSH_SERVICE = data.BOSH_SERVICE;
            jarnxmpp.pubsub_jid = data.pubsub_jid;
            jarnxmpp.jid = data.jid;
            jarnxmpp.connection = new Strophe.Connection(jarnxmpp.BOSH_SERVICE);
            jarnxmpp.connection.attach(jarnxmpp.jid, data.sid, data.rid, jarnxmpp.onConnect);
        });
    });

})(window.jarnxmpp = window.jarnxmpp || {}, jQuery);

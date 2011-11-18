/*global $:false, document:false, window:false, portal_url:false,
jarnxmpp:false, $msg:false, Strophe:false */

$.fn.magicLinks = function () {
    $('a.magic-link', this).each(function () {
        var $link = $(this);
        $link.hide();
        $link.children('.magic-favicon').hide();
        var setLink = function(data) {
            $link.children('.magic-link-title').html(data.title);
            $link.children('.magic-link-descr').html(data.description);
            $link.children('.magic-favicon').attr('src', '/fav-icons?url='+data.favicon_url);
            $link.children('.magic-favicon').show();
            $link.show();
        };
        if (jarnxmpp.Storage.storage !==null && 'ml' + $link.attr('href') in jarnxmpp.Storage.storage) {
            var data = jarnxmpp.Storage.get('ml' + $link.attr('href'));
            setLink(data);
        } else {
            $.getJSON(portal_url + "/magic-links?url=" + $link.attr('href'), function (data) {
                if (data===null) return;
                if (jarnxmpp.Storage.storage!==null) {
                    jarnxmpp.Storage.set('ml' + $link.attr('href'), data);
                }
                setLink(data);
            });
        }
    });
};

$.fn.prettyDate = function () {
    $(this).each(function (idx, el) {
        var d = $(el).attr('data-time');
        if (typeof(d) === 'undefined')
            return true;
        var date = new Date(d),
            diff = (((new Date()).getTime() - date.getTime()) / 1000),
            day_diff = Math.floor(diff / 86400),
            pretty_date;
        if ( isNaN(day_diff) || day_diff < 0 || day_diff >= 31 )
            return true;
        pretty_date =
            day_diff === 0 && (
                diff < 60 && jarnxmpp.UI._('just now') ||
                diff < 120 && jarnxmpp.UI._('1 minute ago') ||
                diff < 3600 && jarnxmpp.UI._('${count} minutes ago', {count: Math.floor( diff / 60 )}) ||
                diff < 7200 && jarnxmpp.UI._('1 hour ago') ||
                diff < 86400 && jarnxmpp.UI._('${count} hours ago', {count: Math.floor( diff / 3600 )})
            ) ||
            day_diff == 1 && jarnxmpp.UI._('yesterday') ||
            day_diff < 7 && jarnxmpp.UI._('${count} days ago', {count: day_diff}) ||
            day_diff < 31 && jarnxmpp.UI._('${count} weeks ago', {count: Math.ceil( day_diff / 7 )});
        $(el).text(pretty_date);
    });
};

jarnxmpp.UI = {

    _: null,
    msg_counter: 0,
    geocoder: null,

    //
    // New message notification
    //
    focus: function() {
        window.blur();
        window.focus();
    },

    updateMsgCounter: function() {
        if (jarnxmpp.UI.msg_counter > 0) {
            if (document.title.search(/^\(\d\) /) === -1) {
                document.title = "(" + jarnxmpp.UI.msg_counter + ") " + document.title;
            }
            else {
                document.title = document.title.replace(/^\(\d\) /, "(" + jarnxmpp.UI.msg_counter + ") ");
            }
            setTimeout(jarnxmpp.UI.focus, 0);
        } else if (document.title.search(/^\(\d\) /) !== -1) {
            document.title = document.title.replace(/^\(\d\) /, "");
        }
    },

    updatePrettyDates: function() {
        $('.prettyDate').prettyDate();
        setTimeout(jarnxmpp.UI.updatePrettyDates, 60000);
    },

    //
    // Geocoding and maps
    //
    _loadGoogleMapsAPI: function (callback) {
        _initGoogleMaps = function() {
            jarnxmpp.UI.geocoder = new google.maps.Geocoder();
            callback();
        };
        if (jarnxmpp.UI.geocoder === null) {
            var hasSensor = 'false',
                userAgent = navigator.userAgent;
            if (userAgent.indexOf('iPhone') != -1 || userAgent.indexOf('Android') != -1 )
                hasSensor = 'true';

            var $script = $("<script>")
                .attr('id', 'google-maps-js')
                .attr('type', 'text/javascript')
                .attr('src', '//maps.googleapis.com/maps/api/js?' +
                             'sensor=' + hasSensor + '&callback=_initGoogleMaps');
            $('body').append($script);
        } else
            callback();
    },

    showGoogleMap: function(id, lat, lng) {
        lat = parseFloat(lat);
        lng = parseFloat(lng);
        var latlng = new google.maps.LatLng(lat, lng),
            options = {
          zoom: 15,
          center: latlng,
          navigationControlOptions: {style: google.maps.NavigationControlStyle.SMALL},
          mapTypeId: google.maps.MapTypeId.ROADMAP
        };
        $('#'+id).css({'width':'280px', 'height':'200px'});
        var map = new google.maps.Map(document.getElementById(id), options);
        $('#' +id).hide();
        $('#' +id).slideDown("slow");
    },

    reverseGeocode: function(lat, lng, callback) {
        lat = parseFloat(lat);
        lng = parseFloat(lng);
        var latlng = new google.maps.LatLng(lat, lng);
        jarnxmpp.UI.geocoder.geocode({'latLng': latlng}, function(results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                var components = {},
                    result = '';
                for (var i=0; i<results[0].address_components.length; i++)
                    components[results[0].address_components[i].types[0]] = results[0].address_components[i].long_name;
                if (components.administrative_area_level_3)
                    result += components.administrative_area_level_3 + ', ';
                if (components.administrative_area_level_2)
                    result += components.administrative_area_level_2 + ', ';
                if (components.administrative_area_level_1)
                    result += components.administrative_area_level_1 + ', ';
                result += components.country;
                callback(result);
            }
        });
    }
};

//
// Presence handler
//
$(document).bind('jarnxmpp.presence', function (event, jid, status, presence) {
    var user_id = Strophe.getNodeFromJid(jid),
        barejid = Strophe.getBareJidFromJid(jid),
        existing_user_element = $('#online-users-' + user_id);
    if (existing_user_element.length) {
        if (status === 'offline' && jarnxmpp.Presence.online.hasOwnProperty(user_id)) {
            return;
        }
        existing_user_element.attr('class', status);
    } else {
        $.get(portal_url + '/xmpp-userDetails?jid=' + barejid, function (user_details) {
            if ($('#online-users-' + user_id).length > 0) {
                return;
            }
            user_details = $(user_details);
            // Put users in alphabetical order. This is stupidly done but works.
            var name = $('a.user-details-toggle', user_details).text().trim(),
                existing_users = $('#online-users > li'),
                added = false;
            $.each(existing_users, function (index, li) {
                var existing_name = $('a.user-details-toggle', li).text().trim();
                if (existing_name > name) {
                    user_details.insertBefore($(li));
                    added = true;
                    return false;
                }
            });
            if (!added) {
                $('#online-users').append(user_details);
            }
        });
        // Pre-fetch user info if we have a session storage.
        if (jarnxmpp.Storage.storage !== null)
            jarnxmpp.Presence.getUserInfo(user_id, function (data) {});
    }
    $('#online-count').text(jarnxmpp.Presence.onlineCount());
});

//
// Message handler
//
$(document).bind('jarnxmpp.message', function (event) {
    var user_id = Strophe.getNodeFromJid(event.from),
        jid = Strophe.getBareJidFromJid(event.from),
        $text_p = $('<p>').html(event.body),
        $form = $('#online-users li#online-users-' + user_id + ' .replyForm').clone(),
        $reply_p = $('<p>').append($form),
        text = $('<div>').append($text_p).append($reply_p).remove().html();
    $('input[type="submit"]', $form).attr('value', 'Reply');

    jarnxmpp.Presence.getUserInfo(user_id, function (data) {
        var gritter_id = $.gritter.add({
            title: data.fullname,
            text: text,
            image: data.portrait_url,
            sticky: true,
            after_close: function () {
                if (jarnxmpp.UI.msg_counter > 1)
                    jarnxmpp.UI.msg_counter -= 1;
                else
                    jarnxmpp.UI.msg_counter = 0;
                jarnxmpp.UI.updateMsgCounter();
            }
        });
        // Let the form know the gritter id so that we can easily close it later.
        $('#gritter-item-' + gritter_id + ' form').attr('data-gritter-id', gritter_id);
        
        jarnxmpp.UI.msg_counter += 1;
        jarnxmpp.UI.updateMsgCounter();
    });
});

//
// PubSub handler
//
$(document).bind('jarnxmpp.pubsubEntryPublished', function (event) {
    var i, isLeaf, $li;
    // If we are showing a feed already, and the item should be in it,
    // inject it.
    jarnxmpp.Storage.xmppGet('last_read_stream_on', function (date) {
        if (date<event.updated)
            $('#site-stream-link').addClass('newStreamMessage');
    });
    if ($('.pubsubNode[data-node="people"]').length > 0 ||
        $('.pubsubNode[data-node=event.node]').length > 0) {
        isLeaf = ($('.pubsubNode[data-node="people"]').length > 0) ? false : true;
        $.get(portal_url + '/@@pubsub-item?',
              {node: event.node,
               id: event.id,
               content: event.content,
               author: event.author,
               published: event.published,
               updated: event.updated,
               geolocation: event.geolocation,
               isLeaf: isLeaf}, function (data) {
                    $li = $('<li>').addClass('pubsubItem').css('display', 'none').html(data);
                    $('.pubsubNode').prepend($li);
                    $('.pubsubNode li:first').slideDown("slow");
                    $('.pubsubNode li:first .prettyDate').prettyDate();
                    $('.pubsubNode li:first').magicLinks();
        });
    }
});

//
// Logging
//
$(document).bind('jarnxmpp.dataReceived', function (ev) {
    $('#xmpp-log').append($('<div>').addClass('xmpp-dataRcvd').text(ev.text));
});

$(document).bind('jarnxmpp.dataSent', function (ev) {
    $('#xmpp-log').append($('<div>').addClass('xmpp-dataSent').text(ev.text));
});

$(document).ready(function () {

    //
    // Load i18n translations
    //
    jarn.i18n.loadCatalog('jarn.xmpp.core.js');
    jarnxmpp.UI._ = jarn.i18n.MessageFactory('jarn.xmpp.core.js');

    //
    // Online users viewlet
    //
    $('a#toggle-online-users').bind('click', function (e) {
        if ($("div#online-users-container").is(':visible')) {
            $("div#online-users-container").hide();
            $('a.user-details-toggle').removeClass('expanded');
        }
        else {
            $("div#online-users-container").show();
        }
        e.preventDefault();
    });

    $('a.user-details-toggle').live('click', function (e) {
        $('a.user-details-toggle').removeClass('expanded');
        $(this).toggleClass('expanded');
        $(this).next().find('[name="message"]:input').focus();
        e.preventDefault();
    });

    if (jarnxmpp.Storage.storage !==null) {
        var count = jarnxmpp.Storage.get('online-count');
        if (count !== null) {
            $('#online-count').text(count);
        }
    }

    //
    // Send message
    //
    $('.sendXMPPMessage').live('submit', function (e) {
        var $field = $('[name="message"]:input', this),
            text = $field.val(),
            recipient = $field.attr('data-recipient'),
            message;
            $(this).parents('.user-details-form')
                   .parent()
                   .children('.user-details-toggle')
                   .removeClass('expanded');
            var gritter_id = $(this).attr('data-gritter-id');
            if (typeof(gritter_id) !== 'undefined')
                $.gritter.remove(gritter_id);
            $("div#online-users-container.autohide").hide('slow');
            $field.val('');
        $.getJSON(portal_url + '/content-transform?', {text: text}, function (data) {
            message = $msg({to: recipient, type: 'chat'}).c('body').t(data.text);
            jarnxmpp.connection.send(message);
        });
        e.preventDefault();
    });

    //
    // PubSub
    //
    $('#pubsub-form input[name="share-location"]').change(function () {
        if ($(this).attr('checked')) {
            var $checkbox = $(this);
            $('div.discreet', $checkbox.parent()).remove();
            navigator.geolocation.getCurrentPosition(
                function(success) {},
                function(error) {
                    $checkbox.attr('checked', false);
                    $checkbox.parent().append(
                        $('<div>').text(jarnxmpp.UI._('Cannot determine your location. Please allow this site to track your location in your browser settings.')).addClass('discreet'));
                }, {maximumAge:600000});
        }
    });

    $('#pubsub-form').bind('submit', function (e) {
        var $field = $('[name="message"]:input', this),
            text = $field.attr('value'),
            node = $field.attr('data-node'),
            share_location = $('input[name="share-location"]', this).attr('checked');

        if (share_location && navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(geolocation) {
                    jarnxmpp.PubSub.publish(node, text, geolocation);
                    $field.attr('value', '');
                },
                function(error) {});
        } else {
            jarnxmpp.PubSub.publish(node, text, null);
            $field.attr('value', '');
        }
        return false;
    });

    $('.replyForm').find('> a').live('click', function (e) {
        $(this).hide();
        $(this).next('form.sendXMPPMessage').fadeIn('medium');
        $(this).next('form.sendXMPPMessage').find('[name="message"]:input').focus();
        e.preventDefault();
    });

    $('.location').live('click', function (e) {
        $locelem = $(this);
        var map_id = $locelem.parent().find('.map').attr('id');
        if ($('#' + map_id).is(':hidden')) {
            jarnxmpp.UI._loadGoogleMapsAPI(function () {
                var latitude = $locelem.attr('data-latitude'),
                    longitude = $locelem.attr('data-longitude');
                jarnxmpp.UI.reverseGeocode(latitude, longitude, function(city) {
                    $locelem.text(city);
                });
                jarnxmpp.UI.showGoogleMap(map_id, latitude, longitude);
            });
        } else {
            $('#' + map_id).hide();
            $locelem.text('');
        }
    });

    $('#share-geolocation').each(function () {
        if (navigator.geolocation)
            $(this).show();
    });

    $('.pubsubNode').magicLinks();
    jarnxmpp.UI.updatePrettyDates();

    //
    // User profile
    //
    $('#xmpp-user-profile #vCard-form button[name="updateVCard"]').click(function () {
        var user_id = Strophe.getNodeFromJid(jarnxmpp.connection.jid);
        $.getJSON(portal_url+"/xmpp-userinfo?user_id="+user_id, function(data) {
            jarnxmpp.vCard.setVCard({FN: data.fullname}, data.portrait_url);
        });
        return false;
    });
});

//
// Initialization after connect.
//

$(document).bind('jarnxmpp.connected', function () {

    // Load my stream.
    $('.pubsubNode').each(function () {
        // If this doesn't have a data-node it must a personal stream.
        if (!$(this).attr('data-node')) {
            $node = $(this);
            jarnxmpp.Storage.xmppSet('last_read_stream_on', jarnxmpp.PubSub._ISODateString(new Date()));
            jarnxmpp.PubSub.getSubscriptions(function (following) {
                $.ajax({url: '/@@pubsub-items',
                        data: {nodes: following},
                        dataType: 'html',
                        traditional:true,
                        success: function (data) {
                            $node.hide();
                            $node.html(data);
                            $node.magicLinks();
                            $node.slideDown("slow");
                        }
                });
            });
        }
    });

    //
    // User profile
    //
    $('#xmpp-user-profile #pubsub-subscriptions').each(function () {
        jarnxmpp.PubSub.getNodes('people', function (available_nodes) {
            var my_node = Strophe.getNodeFromJid(jarnxmpp.connection.jid),
                idx = available_nodes.indexOf(my_node);
            if (idx!==-1) available_nodes.splice(idx, 1);
            $.each(available_nodes, function (idx, node) {
                $('#subscriptions-list').append($('<option>').text(node).attr('value', node));
                jarnxmpp.Presence.getUserInfo(node, function (info) {
                    if (info) {
                        $('#subscriptions-list option[value=' + node + ']').text(info.fullname);
                    } else {
                        $('#subscriptions-list option[value=' + node + ']').remove();
                    }
                });
            });
            jarnxmpp.PubSub.getSubscriptions(function (subscribed_nodes) {
                if (subscribed_nodes.indexOf('people')!==-1) {
                    $('#follow-all').attr('checked', 'checked');
                    $('#subscriptions-list').attr('disabled', true);
                }
                $.each(subscribed_nodes, function (idx, node) {
                    $('#subscriptions-list option[value=' + node +']').attr('selected', 'selected');
                });
            });
        });
    });

    $('#xmpp-user-profile #follow-all').click(function () {
        if ($(this).attr('checked')) {
            $('#subscriptions-list').attr('disabled', true);
            $('#xmpp-user-profile #subscriptions-list').val([]);
            jarnxmpp.PubSub.getSubscriptions(function (following) {
                $(following).each(function (idx, node) {
                    jarnxmpp.PubSub.unsubscribe(node, null, function (result) {});
                });
                jarnxmpp.PubSub.subscribe('people', function (result) {
                    $.gritter.add({title: jarnxmpp.UI._('Subscription updated'),
                                   text: jarnxmpp.UI._('You now follow everybody'),
                                   time: 5000,
                                   sticky: false});
                });
            });
        } else {
            $('#subscriptions-list').attr('disabled', false);
            jarnxmpp.PubSub.unsubscribe('people', null, function (result) {
                $.gritter.add({title: jarnxmpp.UI._('Subscription updated'),
                               text: jarnxmpp.UI._('You now follow noone and can individually select who to follow'),
                               time: 5000,
                               sticky: false});
            });
            jarnxmpp.PubSub.subscribe(Strophe.getNodeFromJid(jarnxmpp.connection.jid), function (result) {});
        }
    });

    $('#xmpp-user-profile #subscriptions-list').change(function () {
        var tofollow = $(this).val() || [];
        jarnxmpp.PubSub.getSubscriptions(function (following) {
            var my_node = Strophe.getNodeFromJid(jarnxmpp.connection.jid),
                idx = following.indexOf(my_node);
            if (idx!==-1) following.splice(idx, 1);
            var subscribe_to = tofollow.filter(function(node) { return following.indexOf(node) < 0; }),
                unsubscribe_from = following.filter(function(node) { return tofollow.indexOf(node) < 0; }),
                fullname;
            $(subscribe_to).each(function (idx, node) {
                jarnxmpp.PubSub.subscribe(node, function (result) {
                    fullname = $('#subscriptions-list option[value=' + node + ']').text();
                    $.gritter.add({title: jarnxmpp.UI._('Subscription updated'),
                                   text: jarnxmpp.UI._('You now follow ${person}', {person: fullname}),
                                   time: 5000,
                                   sticky: false});
                    });
            });
            $(unsubscribe_from).each(function (idx, node) {
                jarnxmpp.PubSub.unsubscribe(node, null, function (result) {
                    fullname = $('#subscriptions-list option[value=' + node + ']').text();
                    $.gritter.add({title: jarnxmpp.UI._('Subscription updated'),
                                   text: jarnxmpp.UI._('You no longer follow ${person}', {person: fullname}),
                                   time: 5000,
                                   sticky: false});
                    });
            });

        });
    });
});

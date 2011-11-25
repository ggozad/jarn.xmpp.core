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

$.fn.sortElements = (function(){
    var sort = [].sort;
    return function(comparator, getSortable) {
        getSortable = getSortable || function(){return this;};
        var placements = this.map(function(){
            var sortElement = getSortable.call(this),
                parentNode = sortElement.parentNode,
                nextSibling = parentNode.insertBefore(
                    document.createTextNode(''),
                    sortElement.nextSibling
                );
            return function() {
                parentNode.insertBefore(this, nextSibling);
                parentNode.removeChild(nextSibling);
            };
        });
        return sort.call(this, comparator).each(function(i){
            placements[i].call(getSortable.call(this));
        });
    };
})();

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
        existing_user_element = $('#online-users-' + user_id),
        online_count;
    if (barejid == Strophe.getBareJidFromJid(jarnxmpp.connection.jid))
        return;
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
            // Set-up following link.
            jarnxmpp.PubSub.getSubscriptions(function (following) {
                $following = $('a.followingStatus', user_details);
                if (following.indexOf('people')!==-1) {
                    $following.remove();
                    return;
                }
                if (following.indexOf(user_id)===-1)
                     $following.text(jarnxmpp.UI._('Follow user'));
                else
                    $following.text(jarnxmpp.UI._('Unfollow user'));
            });
            $('#online-users').append(user_details);
            $('#online-users li[data-userid]').sortElements(function (a, b) {
                return $('a.user-details-toggle', a).text().trim() > $('a.user-details-toggle', b).text().trim() ? 1 : -1;
            });
        });
        // Pre-fetch user info if we have a session storage.
        if (jarnxmpp.Storage.storage !== null)
            jarnxmpp.Presence.getUserInfo(user_id, function (data) {});
    }
    online_count = jarnxmpp.Presence.onlineCount();
    if (online_count>0)
        $('#no-users-online').hide();
    else
        $('#no-users-online').show();
    $('#online-count').text(online_count);
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
    // If we are showing a feed already, and the item should be in it,
    // inject it.
    if (event.pnode)
        return;
    jarnxmpp.Storage.xmppGet('last_read_stream_on', function (date) {
        if (date>event.updated)
            return;
        $('#site-stream-link').addClass('newStreamMessage');
        $('.pubsubNode[data-node*=' + event.node + '], .pubsubNode[data-node=people]').each(function (idx, node) {
            var $li,
                $node = $(node),
                isLeaf = $node.attr('data-leaf') === 'True';
            $('#site-stream-link').removeClass('newStreamMessage');
            jarnxmpp.Storage.xmppSet('last_read_stream_on', jarnxmpp.PubSub._ISODateString(new Date()));
            $.get(portal_url + '/@@pubsub-item?',
                  {node: event.node,
                   id: event.id,
                   content: event.content,
                   author: event.author,
                   published: event.published,
                   updated: event.updated,
                   geolocation: event.geolocation,
                   isLeaf: isLeaf}, function (data) {
                       $('#'+event.id).parent().remove();
                       $li = $('<li>').addClass('pubsubItem').css('display', 'none').html(data);
                       $node.prepend($li);
                       $li.slideDown("slow");
                       $('li:first .prettyDate', $node).prettyDate();
                       $('li:first', $node).magicLinks();
            });
        });
    });
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
    // People online viewlet
    //
    $('a#toggle-online-users').bind('click', function (e) {
        $(this).toggleClass('active');
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
    // Follow/unfollow user.
    $('a.followingStatus').live('click', function (e) {
            var $following_link = $(this),
                node_id = $following_link.attr('data-user'),
                fullname = $following_link.attr('data-fullname');
            jarnxmpp.PubSub.getSubscriptions(function (following) {
                if (following.indexOf(node_id)>-1) {
                    jarnxmpp.PubSub.unsubscribe(node_id, null, function (result) {
                        $following_link.text(jarnxmpp.UI._('Follow user'));
                        $.gritter.add({title: jarnxmpp.UI._('Subscription updated'),
                                       text: jarnxmpp.UI._('You no longer follow ${person}', {person: fullname}),
                                       time: 5000,
                                       sticky: false
                        });
                    });
                } else {
                    jarnxmpp.PubSub.subscribe(node_id, function (result) {
                        $following_link.text(jarnxmpp.UI._('Unfollow user'));
                        $.gritter.add({title: jarnxmpp.UI._('Subscription updated'),
                                       text: jarnxmpp.UI._('You now follow ${person}', {person: fullname}),
                                       time: 5000,
                                       sticky: false});
                    });
                }
            });
            e.preventDefault();
        });

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

    $('.replyForm').find('> a').live('click', function (e) {
        $(this).hide();
        $(this).next('form.sendXMPPMessage').fadeIn('medium');
        $(this).next('form.sendXMPPMessage').find('[name="message"]:input').focus();
        e.preventDefault();
    });

    //
    // PubSub
    //
    $('.pubsub-form input[name="share-location"]').change(function () {
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

    $('.pubsub-form').live('submit', function (e) {
        var $field = $('[name="message"]:input', this),
            text = $field.attr('value'),
            node = $field.attr('data-post-node'),
            pnode = $('input[name="parent"]', this).val(),
            share_location = $('input[name="share-location"]', this).attr('checked');

        if (share_location && navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(geolocation) {
                    jarnxmpp.PubSub.publish(node, pnode, text, geolocation);
                    $field.attr('value', '');
                },
                function(error) {});
        } else {
            jarnxmpp.PubSub.publish(node, pnode,  text, null);
            $field.attr('value', '');
        }
        return false;
    });

    $('.commentOnThread').live('click', function () {
        // If there is already a comment form in this thread close it
        var existing_form = $('.pubsub-form', $(this).parent());
        if (existing_form.length) {
            existing_form.remove();
            return false;
        }
        $('.pubsubNode .pubsub-form').remove();
        var form = $('.pubsub-form').first().clone();
        $('input[name="parent"]', form).val($(this).parent().attr('id'));
        $(this).parent().append(form);
        form.hide();
        form.slideDown('fast');
        return false;
    });

    $('button[name="loadMore"]').click(function () {
        var curr_offset = $('li.pubsubItem:last').offset().top;
        var $node = $('.pubsubNode').first(),
            nodes = $node.attr('data-node').split(' ');
            start = $('li.pubsubItem', $node).length;
            $.ajax({url: portal_url + '/@@pubsub-items',
                    data: {nodes: nodes, start:start},
                    dataType: 'html',
                    traditional:true,
                    success: function (data) {
                        $node.append(data);
                        $('.prettyDate', $node).prettyDate();
                        $node.magicLinks();
                        if ($(data)
                            .filter(function() { return this.nodeType !== 3;})
                            .length <20) $('.loadMoreToggle').remove();
                    }
            });
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

    $('.share-geolocation').each(function () {
        if (navigator.geolocation)
            $(this).show();
    });

    $('.pubsubNode').magicLinks();
    jarnxmpp.UI.updatePrettyDates();

    //
    // User profile
    //
    $('#vCard-form button[name="updateVCard"]').click(function () {
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
            var $node = $(this);
            jarnxmpp.Storage.xmppSet('last_read_stream_on', jarnxmpp.PubSub._ISODateString(new Date()));
            jarnxmpp.PubSub.getSubscriptions(function (following) {
                $node.attr('data-node', following.join(' '));
                $.ajax({url: portal_url + '/@@pubsub-items',
                        data: {nodes: following},
                        dataType: 'html',
                        traditional:true,
                        success: function (data) {
                            $node.hide();
                            $node.html(data);
                            $node.magicLinks();
                            $('.prettyDate', $node).prettyDate();
                            $node.slideDown("slow");
                        }
                });
            });
        }
    });

    //
    // User profile
    //
    $('#subscriptions-form').each(function () {
        jarnxmpp.PubSub.getNodes('people', function (available_nodes) {
            var my_node = Strophe.getNodeFromJid(jarnxmpp.connection.jid),
                idx = available_nodes.indexOf(my_node),
                $sl = $('#subscriptions-list');
            if (idx!==-1) available_nodes.splice(idx, 1);
            $.each(available_nodes, function (idx, node) {
                $sl.append($('<label />')
                            .append($('<input type="checkbox" name="subscriptions:list" />')
                                        .attr('value', node)));
                jarnxmpp.Presence.getUserInfo(node, function (info) {
                    if (info) {
                        $('input[value=' + node + ']', $sl).after(info.fullname);
                    } else {
                        $('input[value=' + node + ']', $sl).parent().remove();
                    }
                });
            });
            $('#subscriptions-list label').sortElements(function(a, b) {
                return $(a).text() > $(b).text() ? 1 : -1;
            });
            jarnxmpp.PubSub.getSubscriptions(function (subscribed_nodes) {
                if (subscribed_nodes.indexOf('people')!==-1) {
                    $('#follow-all').attr('checked', 'checked');
                    $sl.addClass('disabledField');
                    $('input', $sl).attr('disabled', 'disabled');
                }
                else {
                    $('#follow-selected').attr('checked', 'checked');
                }
                $.each(subscribed_nodes, function (idx, node) {
                    $('input[value=' + node +']', $sl)
                        .attr('checked', 'checked')
                        .parent().addClass('subscribed');
                });
            });
        });
    });

    $('input[name="globalFollow"]').bind('change', function () {
        if ($(this).attr('id') === 'follow-selected') {
            $('#subscriptions-list').removeClass('disabledField');
            $('#subscriptions-list input').removeAttr('disabled');
            jarnxmpp.PubSub.unsubscribe('people', null, function (result) {
                $.gritter.add({title: jarnxmpp.UI._('Subscription updated'),
                               text: jarnxmpp.UI._('You now follow noone and can individually select who to follow'),
                               time: 5000,
                               sticky: false});
            });
            jarnxmpp.PubSub.subscribe(Strophe.getNodeFromJid(jarnxmpp.connection.jid), function (result) {});
        }
        else {
            $('#subscriptions-list').addClass('disabledField');
            $('#subscriptions-list input')
                .attr('disabled', 'disabled')
                .removeAttr('checked')
                .parent().removeClass('subscribed');
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
        }
    });

    $('input[name="subscriptions:list"]').live('change', function () {
        var node = this.value,
            $that = $(this);
        if (this.checked) {
            jarnxmpp.PubSub.subscribe(node, function (result) {
                $that.parent().addClass('subscribed');
                fullname = $that.parent().text();
                $.gritter.add({title: jarnxmpp.UI._('Subscription updated'),
                               text: jarnxmpp.UI._('You now follow ${person}', {person: fullname}),
                               time: 5000,
                               sticky: false});
            });
        }
        else {
            jarnxmpp.PubSub.unsubscribe(node, null, function (result) {
                $that.parent().removeClass('subscribed');
                fullname = $that.parent().text();
                $.gritter.add({title: jarnxmpp.UI._('Subscription updated'),
                               text: jarnxmpp.UI._('You no longer follow ${person}', {person: fullname}),
                               time: 5000,
                               sticky: false});
            });
        }
    });
});

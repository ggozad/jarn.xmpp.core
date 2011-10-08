/*global $:false, document:false, window:false, portal_url:false,
jarnxmpp:false, $msg:false, Strophe:false */

// Presence handler

$(document).bind('jarnxmpp.presence', function (event, jid, status, presence) {
    var user_id = Strophe.getNodeFromJid(jid),
        barejid = Strophe.getBareJidFromJid(jid),
        existing_user_element = $('#online-users-' + user_id),
        counter = 0,
        user;
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
    }
    for (user in jarnxmpp.Presence.online) {
        if (jarnxmpp.Presence.online.hasOwnProperty(user)) {
            counter += 1;
        }
    }
    $('#online-count').text(counter);
});

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
            sticky: true
        });
        // Let the form know the gritter id so that we can easily close it later.
        $('#gritter-item-' + gritter_id + ' form').attr('data-gritter-id', gritter_id);
    });
});

// Pub-Sub
$(document).bind('jarnxmpp.pubsubEntryPublished', function (event) {
    var i, isLeaf, $li;
    // Put some stupid animation and let Denys fix it.
    $('#site-stream-link').addClass('newStreamMessage');
    // If we are showing a feed already, and the item should be in it,
    // inject it.
    if ($('.pubsubNode[data-node="people"]').length > 0 ||
        $('.pubsubNode[data-node=event.node]').length > 0) {
        isLeaf = ($('.pubsubNode[data-node="people"]').length > 0) ? false : true;
        $.get(portal_url + '/@@pubsub-item?',
              {node: event.node,
               item_id: event.item_id,
               content: event.content,
               author: event.author,
               published: event.published,
               updated: event.updated,
               isLeaf: isLeaf}, function (data) {
            $li = $('<li>').addClass('pubsubItem').css('display', 'none').html(data);
            $('.pubsubNode').prepend($li);
            $('.pubsubNode li:first').slideDown("slow");
            $('.pubsubNode li:first').magicLinks();
        });
    }
});

// Logging

$(document).bind('jarnxmpp.dataReceived', function (ev) {
    $('#xmpp-log').append($('<div>').addClass('xmpp-dataRcvd').text(ev.text));
});

$(document).bind('jarnxmpp.dataSent', function (ev) {
    $('#xmpp-log').append($('<div>').addClass('xmpp-dataSent').text(ev.text));
});

$.fn.magicLinks = function () {
    $('a.magic-link', this).each(function () {
        var $link = $(this);
        $link.hide();
        $link.children('.magic-favicon').hide();
        var setLink = function(data) {
            $link.children('.magic-link-title').html(data.title);
            $link.children('.magic-link-descr').html(data.description);
            $link.children('.magic-favicon').attr('src', data.favicon_url);
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

$(document).ready(function () {

    $('.sendXMPPMessage').live('submit', function (e) {
        var $field = $('input[name="message"]', this),
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
            $("ul#online-users").removeClass('activated');
            $field.val('');
        $.getJSON(portal_url + '/content-transform?', {text: text}, function (data) {
            message = $msg({to: recipient, type: 'chat'}).c('body').t(data.text);
            jarnxmpp.connection.send(message);
        });
        e.preventDefault();
    });

    $('a#toggle-online-users').bind('click', function (e) {
        if ($("ul#online-users").hasClass('activated')) {
            $("ul#online-users").removeClass('activated');
            $('a.user-details-toggle').removeClass('expanded');
        }
        else {
            $("ul#online-users").addClass('activated');
        }
        e.preventDefault();
    });

    $('a.user-details-toggle').live('click', function (e) {
        $('a.user-details-toggle').removeClass('expanded');        
        $(this).toggleClass('expanded');
        $(this).next().find('input[name="message"]').focus();
        e.preventDefault();
    });

    $('#pubsub-form').bind('submit', function (e) {
        var $field = $('input[name="message"]', this),
            text = $field.attr('value'),
            node = $field.attr('data-node');
        jarnxmpp.PubSub.publishToPersonalNode(node, text);
        $field.attr('value', '');
        return false;
    });

    $('.replyForm').find('> a').live('click', function (e) {
        $(this).hide();
        $(this).next('form.sendXMPPMessage').fadeIn('medium');
        $(this).next('form.sendXMPPMessage').find('input[name="message"]').focus();        
        e.preventDefault();
    });

    $('.pubsubNode').magicLinks();
});

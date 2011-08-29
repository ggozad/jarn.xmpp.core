/*
    Event handlers
*/

// Presence handler

$(document).bind('jarnxmpp.presence', function (event, jid, status, presence) {
    var user_id = Strophe.getNodeFromJid(jid);
    var barejid = Strophe.getBareJidFromJid(jid);
    var existing_element = $('#online-users-'+user_id);
    if (existing_element.length) {
        if (status==='offline' && jarnxmpp.Presence.online.hasOwnProperty(user_id))
             return;
        existing_element.attr('class', status);
    } else {
        var dd = $('<dd>')
            .attr('class', status)
            .attr('id', 'online-users-'+user_id);
        $('#online-users').append(dd);
        jarnxmpp.Presence.getUserInfo(user_id, function(data) {
            if (data===null) return;
            var portrait = $('<div>').attr('class', 'avatar').append($('<img/>')
                .attr('title', data.fullname)
                .attr('src', data.portrait_url)
                .attr('class','portrait'));
            var actions = $('<div>').attr('class', 'online-user-actions');
            var personalFeed = $('<a>')
                .attr('href', '@@pubsub-feed?node=' + user_id)
                .text(data.fullname);
            var sendMessage = $('<a>')
                .attr('href', 'sendXMPPMessage?message-recipient=' + barejid);
            sendMessage.append($('<img>')
                .attr('src', '++resource++jarn.xmpp.core.images/chat_icon.png')
            );
            sendMessage.prepOverlay({
                subtype: 'ajax',
            });
            dd.append(portrait);
            actions.append($('<div>').append(personalFeed));
            actions.append($('<div>').append(sendMessage));
            dd.append(actions);
        });
    }
    var counter = 0;
    for (var key in jarnxmpp.Presence.online) {
        if (jarnxmpp.Presence.online.hasOwnProperty(key))
            counter++;
    }
    $('#online-count').text(counter);
});

$(document).bind('jarnxmpp.message', function (event) {
    var user_id = Strophe.getNodeFromJid(event.from);
    var jid = Strophe.getBareJidFromJid(event.from);
    var text_p = $('<p>').text(event.body);
    var chat_p = $('<p>');
    var chat_link = $('<a>')
        .attr('class', 'chat-link')
        .attr('href', 'muc?invitee=' + jid)
        .text('Chat');
    chat_p.append(chat_link);
    var text = $('<div>').append(text_p).append(chat_p).remove().html();
    jarnxmpp.Presence.getUserInfo(user_id, function(data) {
        $.gritter.add({
            title: data.fullname,
            text: text,
            image: data.portrait_url,
            sticky: true,
            after_open: function (e) {
                e.find('.chat-link').prepOverlay({
                    subtype: 'ajax'
                });
            }
        });
    });
});

// Pub-Sub
$(document).bind('jarnxmpp.nodePublished', function (event) {
    jarnxmpp.Presence.getUserInfo(event.author, function(data) {
        $.gritter.add({
            title: data.fullname,
            text: event.content,
            image: data.portrait_url
        });
    });
});


// MUC

// Room invites
$(document).bind('jarnxmpp.roomInvitation', function (event) {
    var user_id = Strophe.getNodeFromJid(event.from);
    var link = '@@muc?room=' + event.room;
    var body = 'You have received an invitation to ' +
           '<a class="chat-link" href="'+ link +'">join</a>' +
           ' a group chat.';

    jarnxmpp.Presence.getUserInfo(user_id, function(data) {
        $.gritter.add({
            title: data.fullname,
            text: body,
            image: data.portrait_url,
            sticky: true,
            after_open: function (e) {
                e.find('.chat-link').prepOverlay({
                    subtype: 'ajax',
                });
            },
        });
    });
});

$(document).bind('jarnxmpp.muc.displayPublicMessage', function (ev) {
    var msg = "";
    if (!ev.notice) {
        var delay_css = ev.delayed ? " delayed" : "";
        // messages from ourself will be styled differently
        var nick_class = "nick";
        if (ev.nick === jarnxmpp.muc.nickname)
            nick_class += " self";

        msg = $('<div>').addClass('message').addClass(delay_css);
        msg.append($('<span>')
            .addClass(nick_class)
            .text('<' + ev.nick + '>'));
        msg.append($('<span>')
            .addClass('body')
            .text(ev.body));

    } else
        msg = $('<div>').addClass('notice').text(ev.body);

    // detect if we are scrolled all the way down
    var chat = $('#chat').get(0);
    var at_bottom = chat.scrollTop >= chat.scrollHeight - chat.clientHeight;
    $('#chat').append(msg);
    // if we were at the bottom, keep us at the bottom
    if (at_bottom) {
        chat.scrollTop = chat.scrollHeight;
    }
});

$(document).bind('jarnxmpp.muc.roomJoined', function (ev, owner) {
    jarnxmpp.muc.joined = true;
    $('#room-name').text(jarnxmpp.muc.room);
    var li = $('<li>').attr('id', 'muc-participant-'+owner).text(owner);
    $('#participant-list').append(li);
    $('#muc-online-'+owner).remove();
    var event = jQuery.Event('jarnxmpp.muc.displayPublicMessage');
    event.body = "Room joined";
    event.notice = true;
    $(document).trigger(event);
});

$(document).bind('jarnxmpp.muc.userJoined', function (ev, nick) {
    var li = $('<li>').attr('id', 'muc-participant-'+nick).text(nick);
    $('#participant-list').append(li);
    $('#muc-online-'+nick).remove();
    var event = jQuery.Event('jarnxmpp.muc.displayPublicMessage');
    event.body = nick +" joined.";
    event.notice = true;
    $(document).trigger(event);
});

$(document).bind('jarnxmpp.muc.userLeft', function (ev, nick) {
    $('#muc-participant-'+nick).remove();
    var event = jQuery.Event('jarnxmpp.muc.displayPublicMessage');
    event.body = nick +" left.";
    event.notice = true;
    $(document).trigger(event);
    if (nick in jarnxmpp.Presence.online)
        $(document).trigger('jarnxmpp.muc.userOnline', [nick]);  
});

$(document).bind('jarnxmpp.muc.userOnline', function (ev, nick) {
    if ($('#muc-online-'+nick).length === 0) {
        var li = $('<li>').attr('id', 'muc-online-'+nick);
        li.append($('<span>').text(nick));
        li.append($('<button>').attr('class', 'invite').text('invite'));
        $('#online-list').append(li);
    }
});

$(document).bind('jarnxmpp.muc.userOffline', function (ev, nick) {
    $('#muc-online-'+nick).remove();
});

// Logging

$(document).bind('jarnxmpp.dataReceived', function (ev) {
    $('#xmpp-log').append($('<div>').addClass('xmpp-dataRcvd').text(ev.text));
});

$(document).bind('jarnxmpp.dataSent', function (ev) {
    $('#xmpp-log').append($('<div>').addClass('xmpp-dataSent').text(ev.text));
});

$(document).ready(function () {

    $('#sendXMPPMessage').live('submit', function () {
        var text = $(this).find('textarea[name="message"]').attr('value');
        var recipient = $(this).find('input[name="message-recipient"]').attr('value');
        var message = $msg({to: recipient, type: 'chat'})
            .c('body').t(text);
        jarnxmpp.connection.send(message);
        $(this).parents('.overlay').data('overlay').close();
        return false;
    });

    $('#toggle-online-users').bind('click', function (el) {
        $('#online-users').toggleClass('deactivated');
        return false;
    });

    $('.pubsub-post').prepOverlay({
        subtype: 'ajax'
    });

    $('a.magic-link').each(function () {
        var link = this;
        $(link).hide();
        $(link).children('.magic-favicon').hide();
        $.getJSON(portal_url+"/magic-links?url="+$(link).attr('href'), function(data) {
            $(link).children('.magic-link-title').html(data.title);
            $(link).children('.magic-link-descr').html(data.description);
            $(link).children('.magic-favicon').attr('src', data.favicon_url);
            $(link).children('.magic-favicon').show();
            $(link).show();
        });
    }); 

});

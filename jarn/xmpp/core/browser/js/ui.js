// Messages
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
                    subtype: 'ajax',
                });
            },
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

$(document).ready(function () {
    $('.pubsub-post').prepOverlay({
        subtype: 'ajax',
    });
});

// Online users portlet
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
            .attr('id', 'online-users-'+user_id)
            .attr('title', 'Send message');
        $('#online-users').append(dd);
        jarnxmpp.Presence.getUserInfo(user_id, function(data) {
            if (data===null) return;
            var sendMessage = $('<a>')
                .attr('class', 'online-users-message')
                .attr('href','sendXMPPMessage?message-recipient=' + barejid);
            sendMessage.append($('<img/>').attr('title', data.fullname).attr('src', data.portrait_url));
            sendMessage.prepOverlay({
                subtype: 'ajax',
            });
            dd.append(sendMessage);
        });
    }
});

$(document).ready(function () {
    $('#online-users .online').live('mouseover', function () {
        $("#"+this.id+"[title]").tooltip({position: 'center center',});
    });
    $('#sendXMPPMessage').live('submit', function () {
        var text = $(this).find('input[name="message"]').attr('value');
        var recipient = $(this).find('input[name="message-recipient"]').attr('value');
        var message = $msg({to: recipient, type: 'chat'})
            .c('body').t(text);
        jarnxmpp.connection.send(message);
        $(this).parents('.overlay').data('overlay').close();
        return false;
    });
});

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

// MUC

$(document).bind('jarnxmpp.muc.roomJoined', function (ev, owner) {
    jarnxmpp.muc.joined = true;
    $('#room-name').text(jarnxmpp.muc.room);
    var li = $('<li>').attr('id', 'muc-participant-'+owner).text(owner);
    $('#participant-list').append(li);
    $('#muc-online-'+owner).remove();
    jarnxmpp.muc.addMessage("Room joined.", null, true, false);
});

$(document).bind('jarnxmpp.muc.userJoined', function (ev, nick) {
    var li = $('<li>').attr('id', 'muc-participant-'+nick).text(nick);
    $('#participant-list').append(li);
    $('#muc-online-'+nick).remove();
    jarnxmpp.muc.addMessage(nick +" joined.", null, true, false);
});

$(document).bind('jarnxmpp.muc.userLeft', function (ev, nick) {
    $('#muc-participant-'+nick).remove();
    jarnxmpp.muc.addMessage(nick +" left.", null, true, false);
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
$(document).bind('jarnxmpp.message', function (event) {
    var userid = Strophe.getNodeFromJid(event.from);
    var jid = Strophe.getBareJidFromJid(event.from);
    var text_p = $('<p>').text(event.body);
    var chat_p = $('<p>');
    var chat_link = $('<a class="chat-link" href="muc?invitee=' + jid + '">Chat</a>');

    chat_p.append(chat_link);
    var text = $('<div>').append(text_p).append(chat_p).remove().html();

    var member_info = $.getJSON(portal_url+"/xmpp-userinfo?user_id="+userid, function(data) {
        $.gritter.add({
            title: data.fullname,
            text: text,
            image: data.portrait_url,
            sticky: true,
            after_open: function (e) {
                // e.find('.chat-link').prepOverlay({
                //     subtype: 'ajax',
                // });
            },
        });
    });
});

$(document).bind('jarnxmpp.roomInvitation', function (event) {
    link = portal_url + '/@@muc?room=' + event.room;
    body = 'You have received an invitation to ' +
           '<a class="muc_join" href="'+ link +'">join</a>' +
           ' a group chat.';
    $.gritter.add({
        title: event.from,
        text: body,
        sticky: true,
    });
});

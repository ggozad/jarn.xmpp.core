$(document).bind('jarnxmpp.message', function (event) {
    var userid = Strophe.getNodeFromJid(event.from);
    var jid = Strophe.getBareJidFromJid(event.from);
    var text_p = $('<p>').text(event.body);
    var chat_p = $('<p>');
    var chat_link = $('<a>')
        .attr('class', 'chat-link')
        .attr('href', 'muc?invitee=' + jid)
        .text('Chat');
    chat_p.append(chat_link);
    var text = $('<div>').append(text_p).append(chat_p).remove().html();

    var member_info = $.getJSON(portal_url+"/xmpp-userinfo?user_id="+userid, function(data) {
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

$(document).bind('jarnxmpp.roomInvitation', function (event) {
    var userid = Strophe.getNodeFromJid(event.from);
    var link = '@@muc?room=' + event.room;
    var body = 'You have received an invitation to ' +
           '<a class="chat-link" href="'+ link +'">join</a>' +
           ' a group chat.';

    var member_info = $.getJSON(portal_url+"/xmpp-userinfo?user_id="+userid, function(data) {
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

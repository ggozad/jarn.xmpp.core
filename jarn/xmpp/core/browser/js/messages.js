$(document).bind('jarnxmpp.message', function (event) {
    var userid = Strophe.getNodeFromJid(event.from);
    var member_info = $.getJSON(portal_url+"/xmpp-userinfo?user_id="+userid, function(data) {
        $.gritter.add({
            title: data.fullname,
            text: event.body,
            image: data.portrait_url
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

$(document).ready(function () {
    $('.muc_join').live('click', function () {
        var invitee = $(this).attr('value');
        window.open($(this).attr('href'), "Chat",
                    "menubar=0,resizable=0,width=800,height=500");
    });
});

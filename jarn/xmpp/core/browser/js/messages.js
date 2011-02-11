$(document).bind('pmcxmpp.message', function (event) {
    //XXX If mtype is 'xhtml' we should sanitize
    $.gritter.add({
        title: event.from,
        text: event.body,
    });
});

$(document).bind('pmcxmpp.roomInvitation', function (event) {
    link = portal_url + '/@@muc?room=' + event.room
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

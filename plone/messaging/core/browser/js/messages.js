$(document).bind('pmcxmpp.message', function (event) {
    //XXX If mtype is 'xhtml' we should sanitize
    $.gritter.add({
        title: event.from,
        text: event.body,
    });
});

$(document).bind('pmcxmpp.roomInvitation', function (event) {
    link = portal_url + '/@@muc'
    body = 'You have received an invitation to ' +
           '<a href="' + link +'">join</a>' +
           ' a group chat.';
    $.gritter.add({
        title: event.from,
        text: body,
        sticky: true,
    });
});

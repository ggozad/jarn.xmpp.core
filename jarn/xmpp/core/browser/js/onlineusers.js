$(document).bind('jarnxmpp.presence', function (event, jid, status) {
    userid = Strophe.getNodeFromJid(jid);
    barejid = Strophe.getBareJidFromJid(jid);
    existing = $('#online-users dd').find(":contains("+userid+")");
    existing.parent().remove()
    dd = $('<dd></dd>').addClass("portletItem");
    dd.append($('<button></button>')
        .addClass(status)
        .text('chat')
        .attr('value', barejid));
    dd.append($('<span></span>').addClass(status).text(userid));
    $('#online-users').append(dd);
});

$(document).ready(function () {
    $('button.online').live('click', function () {
        var invitee = $(this).attr('value');
        window.open(portal_url+'/@@muc?invitee=' + invitee, "Chat",
                    "menubar=0,resizable=0,width=800,height=500");
    });
});

$(document).bind('jarnxmpp.presence', function (event, jid, status) {
    var userid = Strophe.getNodeFromJid(jid);
    var barejid = Strophe.getBareJidFromJid(jid);
    var existing = $('#online-users').find('#presence-portlet'+userid);
    if (existing.length > 0) {
        existing.attr('class', status);
    } else {
        member_info = $.getJSON(portal_url+"/xmpp-userinfo?user_id="+userid, function(data) {
            var dd = $('<dd></dd>').attr('class', status).attr('id', 'presence-portlet'+userid);
            dd.append($('<img/>').attr('title', data.fullname).attr('src', data.portrait_url));
            $('#online-users').append(dd);
        });
    }
    // dd.append($('<button></button>')
    //     .addClass(status)
    //     .text('chat')
    //     .attr('value', barejid));
    // dd.append($('<span></span>').addClass(status).text(userid));
});

$(document).ready(function () {
    // $('button.online').live('click', function () {
    //     var invitee = $(this).attr('value');
    //     window.open(portal_url+'/@@muc?invitee=' + invitee, "Chat",
    //                 "menubar=0,resizable=0,width=800,height=500");
    // });
});

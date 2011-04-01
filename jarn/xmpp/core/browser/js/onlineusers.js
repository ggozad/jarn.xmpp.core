$(document).bind('jarnxmpp.presence', function (event, jid, status) {
    var userid = Strophe.getNodeFromJid(jid);
    var barejid = Strophe.getBareJidFromJid(jid);
    var existing = $('#online-users').find('#online-users-'+userid);
    if (existing.length > 0) {
        existing.attr('class', status);
    } else {
        member_info = $.getJSON(portal_url+"/xmpp-userinfo?user_id="+userid, function(data) {
            var dd = $('<dd></dd>').attr('class', status).attr('id', 'online-users-'+userid);
            var ul = $('<ul class="online-users-actions inactive"><li class="online-users-message"><a>Message</a></li><ul>');
            dd.append($('<img/>').attr('title', data.fullname).attr('src', data.portrait_url));
            dd.append(ul);
            $('#online-users').append(dd);
        });
    }
});

$(document).ready(function () {
    $('#online-users .online').live('hover', function () {
        if (event.type === 'mouseover') {
            $(this).find('.online-users-actions').attr('class', 'online-users-actions active');
        } else {
            $(this).find('.online-users-actions').attr('class', 'online-users-actions inactive');
        }
    });
    $('.online-users-message').live('click', function() {
        alert('message');
    });
});

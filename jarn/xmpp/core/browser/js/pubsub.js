$(document).bind('jarnxmpp.nodePublished', function (event) {
    var member_info = $.getJSON(portal_url+"/xmpp-userinfo?user_id="+event.author, function(data) {
        $.gritter.add({
            title: data.fullname,
            text: event.content,
            image: data.portrait_url
        });
    });
});

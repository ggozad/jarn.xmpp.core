pmcxmpp.Presence = {
    presenceReceived: function (presence) {
        var ptype = $(presence).attr('type');
        var from = $(presence).attr('from');
        var status = '';
        if (ptype !== 'error') {
            if (ptype === 'unavailable') {
                status = 'offline';
            } else {
                var show = $(presence).find('show').text(); 
                if (show === '' || show === '') {
                    status = 'online'
                } else {
                    status = 'away'
                }
            } 
        }
        return true;
    }
};

$(document).bind('pmcxmpp.connected', function () {
    pmcxmpp.connection.addHandler(pmcxmpp.Presence.presenceReceived, null, 'presence', null);
    pmcxmpp.connection.send($pres());
});

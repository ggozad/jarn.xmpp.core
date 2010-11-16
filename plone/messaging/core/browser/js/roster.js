pmcxmpp.Roster = {
    rosterSet: function(iq) {
        // XXX: Fill me in
    },
    rosterResult: function(iq) {
        // XXX: Fill me in
    }
};

$(document).bind('pmcxmpp.connected', function () {
    pmcxmpp.connection.addHandler(pmcxmpp.Roster.rosterSet, Strophe.NS.ROSTER, "iq", "set");
    pmcxmpp.connection.addHandler(pmcxmpp.Roster.rosterResult, Strophe.NS.ROSTER, "iq", "result");
    //var roster_iq = $iq({type: 'get'}).c('query', {xmlns: Strophe.NS.ROSTER});
    //pmcxmpp.connection.sendIQ(roster_iq);
});
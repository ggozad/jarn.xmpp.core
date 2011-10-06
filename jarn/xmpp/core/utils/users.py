USER_NODE_CONFIG = {
    'pubsub#collection': 'people',
    'pubsub#max_items': 1000
}


def setupPrincipal(client,
                   principal_jid, principal_password,
                   roster_jids):
    """Create a jabber account for a new user as well
       as create and configure its associated nodes."""

    principal_id = principal_jid.user

    def subscribeToAllUsers(result):
        if result == False:
            return False
        if roster_jids:
            client.chat.sendRosterItemAddSuggestion(principal_jid, roster_jids)
        return True

    def addUserPubSubNode(result):
        if result == False:
            return False
        d = client.createNode(principal_id,
            options=USER_NODE_CONFIG)
        return d

    def affiliateUser(result):
        if result == False:
            return False
        d = client.setNodeAffiliations(principal_id,
                                       [(principal_jid, 'publisher', )])
        return d

    def subscribeToMainFeed(result):
        if result == False:
            return False
        d = client.setSubscriptions('people',
                                    [(principal_jid, 'subscribed', )])
        return d

    d = client.admin.addUser(principal_jid.userhost(), principal_password)
    d.addCallback(subscribeToAllUsers)
    d.addCallback(addUserPubSubNode)
    d.addCallback(affiliateUser)
    d.addCallback(subscribeToMainFeed)
    return d


def deletePrincipal(client, principal_jid):
    """Delete a jabber account as well as remove its associated nodes.
    """
    principal_id = principal_jid.user

    def deleteUser(result):
        if result == False:
            return False
        d = client.admin.deleteUsers(principal_jid.userhost())
        return d

    d = client.deleteNode(principal_id)
    d.addCallback(deleteUser)
    return d

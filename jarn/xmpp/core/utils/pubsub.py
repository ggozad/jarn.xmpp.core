import logging

from twisted.internet import defer


logger = logging.getLogger('jarn.xmpp.core')


def getAllChildNodes(client, root):
    """ XXX TODO:
    This would have been simpler if ejabberd supported retrieving
    collection items as it should. Argue in the mailing list.
    """
    tree = {}

    def getChildNodes(parent):

        def gotNodeTypes(result):
            deferred_list = []
            for success, res in result:
                if success:
                    node, node_type = res
                    if node_type == 'collection':
                        tree[node] = []
                        if parent is not None:
                            tree[parent].append(node)
                        else:
                            tree[''].append(node)
                        deferred_list.append(getChildNodes(node))
                    else:
                        if parent is not None:
                            tree[parent].append(node)
                        else:
                            tree[''].append(node)
            if deferred_list:
                return defer.DeferredList(deferred_list)
            return True

        def gotNodes(result):
            d = defer.DeferredList(
                [client.getNodeType(node_dict['node'])
                 for node_dict in result],
                consumeErrors=True)
            d.addCallback(gotNodeTypes)
            return d

        d = client.getNodes(parent)
        d.addCallback(gotNodes)
        return d

    def returnResult(result):
        return tree

    if root is None:
        tree[''] = []
    else:
        tree[root] = []

    d = getChildNodes(root)
    d.addCallback(returnResult)
    return d

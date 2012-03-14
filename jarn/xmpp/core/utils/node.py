from zope.interface import implements

from jarn.xmpp.core.interfaces import INodeEscaper


class NodeEscaper(object):
    """Implements basic XEP106 escape mechanism."""

    implements(INodeEscaper)

    XEP0106_mapping = [(' ','20'),
                       ('"','22'),
                       ('&','26'),
                       ('\'','27'),
                       ('/','2f'),
                       (':','3a'),
                       ('<','3c'),
                       ('>','3e'),
                       ('@','40')]

      
    def escape(self, node):
        """Replaces all characters disallowed by the Nodeprep profile of
        stringprep using escape mapping.
        """
        if not node:
            return

        node = node.replace('\\5c', '\\5c5c')

        for char, repl in self.XEP0106_mapping:
            node = node.replace('\\%s' % repl, '\\5c%s' % repl)

        for char, repl in self.XEP0106_mapping:
            node = node.replace(char, '\\%s' % repl)

        return node

    def unescape(self, node):
        """Replaces all disallowed characters that were escaped  
        with unescaped ones.
        """

        if not node:
            return

        for char, repl in self.XEP0106_mapping:
              node = node.replace('\\%s' % repl, char)

        return node.replace('\\5c', '\\')


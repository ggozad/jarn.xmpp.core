import unittest
from jarn.xmpp.core.utils.node import NodeEscaper

class NodeEscaperTests(unittest.TestCase):

    jids = [('space cadet@example.com', 'space\\20cadet@example.com'),
            ('call me "ishmael"@example.com',
             'call\\20me\\20\\22ishmael\\22@example.com'),
            ('at&t guy@example.com', 'at\\26t\\20guy@example.com'),
            ('d\'artagnan@example.com', 'd\\27artagnan@example.com'),
            ('/.fanboy@example.com', '\\2f.fanboy@example.com'),
            ('::foo::@example.com', '\\3a\\3afoo\\3a\\3a@example.com'),
            ('<foo>@example.com', '\\3cfoo\\3e@example.com'),
            ('user@host@example.com', 'user\\40host@example.com'),
            ('c:\\net@example.com', 'c\\3a\\net@example.com'),
            ('c:\\net@example.com', 'c\\3a\\net@example.com'),
            ('c:\\cool stuff@example.com', 'c\\3a\\cool\\20stuff@example.com'),
            ('c:\\5commas@example.com', 'c\\3a\\5c5commas@example.com'),
            ('example@example.com', 'example@example.com')]

    def setUp(self):
        self.escaper = NodeEscaper()

    def test_jid_escaping(self):
        for jid in self.jids:
            node, host = tuple(jid[0].rsplit('@', 1))
            self.assertEqual('%s@%s' % (self.escaper.escape(node), host), jid[1])

    def test_jid_unescaping(self):
        for jid in self.jids:
            node, host = tuple(jid[1].rsplit('@', 1))
            self.assertEqual('%s@%s' % (self.escaper.unescape(node), host), jid[0])


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

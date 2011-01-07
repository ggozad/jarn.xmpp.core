import random
import httplib
import base64
from urlparse import urlparse
from xml.dom.minidom import Document, Element, parseString

NS_HTTPBIND = 'http://jabber.org/protocol/httpbind'
NS_TLS = 'urn:ietf:params:xml:ns:xmpp-tls'
NS_SASL = 'urn:ietf:params:xml:ns:xmpp-sasl'
NS_BIND = 'urn:ietf:params:xml:ns:xmpp-bind'
NS_SESSION = 'urn:ietf:params:xml:ns:xmpp-session'
NS_XMPP_BOSH = 'urn:xmpp:xbosh'
NS_JABBER = 'jabber:client'


class BOSHClient(object):

    def __init__(self, jid, password, service):
        self.jid = jid
        self.password = password
        self.headers = {"Content-type": "text/xml", "Accept": "text/xml"}
        self.rid = random.randint(0, 4294967295)
        self.sid = None
        self.bosh_service = urlparse(service)

    def buildBody(self, attributes={}, child=None):


        body = Element('body')
        body.setAttribute('xmlns', NS_HTTPBIND)
        body.setAttribute('rid', str(self.rid))
        body.setAttribute('xml:lang', 'en')
        if self.sid:
            body.setAttribute('sid', self.sid)

        for attribute in attributes:
            body.setAttribute(attribute, attributes[attribute])
        if child is not None:
            body.appendChild(child)
        self.rid = self.rid + 1
        return body

    def sendRequest(self, body):
        conn = httplib.HTTPConnection(self.bosh_service.netloc)
        conn.request("POST",
                     self.bosh_service.path,
                     body.toxml(),
                     self.headers)
        response = conn.getresponse()
        data = None
        if response.status == 200:
            data = parseString(response.read())
        conn.close()
        if not data:
            return False
        return data

    def startSession(self, hold=1, wait=70):
        body = self.buildBody(attributes={
            'content': 'text/xml; charset=utf-8',
            'from': self.jid.userhost(),
            'to': self.jid.host,
            'hold': str(hold),
            'wait': str(wait),
            'window': '7',
            'xmlns:xmpp': NS_XMPP_BOSH,
            'xmpp:version': '1.0'})

        response = self.sendRequest(body)
        if not response:
            return False

        body = response.getElementsByTagName('body')[0]
        if not body.hasAttribute('sid'):
            return False
        self.sid = body.getAttribute('sid')
        mechanism_elems = body.getElementsByTagNameNS(NS_SASL, 'mechanism')
        mechanisms = [elem.firstChild.nodeValue for elem in mechanism_elems]

        if 'PLAIN' in mechanisms:
            return self.authenticatePlain()
        return False

    def authenticatePlain(self):
        dom = Document()
        auth = Element('auth')
        auth.setAttribute('xmlns', NS_SASL)
        auth.setAttribute('mechanism', 'PLAIN')
        auth_str = "\000" + self.jid.user.encode('utf-8') + \
                   "\000" + self.password.encode('utf-8')
        auth_str = base64.encodestring(auth_str)
        auth_str = dom.createTextNode(auth_str)
        auth.appendChild(auth_str)
        body = self.buildBody(child=auth)
        response = self.sendRequest(body)
        if not response or not response.getElementsByTagName('success'):
            return False
        return self.bindResource()

    def bindResource(self):
        body = self.buildBody(attributes={
            'xmpp:restart': 'true',
            'xmlns:xmpp': 'urn:xmpp:xbosh'})
        response = self.sendRequest(body)
        if not response:
            return False
        if not response.getElementsByTagName('bind'):
            return False
        dom = Document()
        iq = Element('iq')
        iq.setAttribute('id', str(random.randint(0, 1000000)))
        iq.setAttribute('type', 'set')
        bind = Element('bind')
        bind.setAttribute('xmlns', NS_BIND)
        resource = Element('resource')
        resource_str = dom.createTextNode(self.jid.resource)
        resource.appendChild(resource_str)
        bind.appendChild(resource)
        iq.appendChild(bind)
        body = self.buildBody(child=iq)
        response = self.sendRequest(body)
        if not response or not response.getElementsByTagName('jid'):
            return False

        iq = Element('iq')
        iq.setAttribute('id', str(random.randint(0, 1000000)))
        iq.setAttribute('type', 'set')
        session = Element('session')
        session.setAttribute('xmlns', NS_SESSION)
        iq.appendChild(session)
        body = self.buildBody(child=iq)
        response = self.sendRequest(body)
        return True

Introduction
============

``jarn.xmpp.core`` is a Plone add-on providing the following functionality based on XMPP services:

* Integration of plone user accounts with XMPP accounts and authentication.
* Basic messaging and multi-user chat.
* A minimal microblogging environment based on XMPP PubSub.

It is part of a suite of packages aiming to provide XMPP services to Plone. The other two packages are

* `jarn.xmpp.twisted`_, provides XMPP-specific protocol implementation for twisted.
* `jarn.xmpp.collaboration`_ provides an XMPP protocol to do real-time collaborative editing as well as a Plone-targeted implementation.

Installation
============

Before setting up the package you need to have a working XMPP server and access to the administration account on the server. The package has only been tested with ejabberd version 2.1.5 and above which is recommended. In any case the following XMPP extensions need to be supported by the server you are going to use:

* `XEP-0071`_ XHTML-IM.
* `XEP-0144`_ Roster Item Exchange.
* `XEP-0060`_ Publish-Subscribe.
* `XEP-0248`_ PubSub Collection Nodes.
* `XEP-0133`_ Service Administration.
* `XEP-0124`_ Bidirectional-streams Over Synchronous HTTP (BOSH)
* `XEP-0206`_ XMPP over BOSH

Buildout
--------
A sample buildout you can use as a starting point can be found at `jarn.xmpp.buildout`_. Wokkel on which ``jarn.xmpp.twisted`` depends upon has not had a release for a while, so you will need to either use a development version or add::

    find-links = http://dist.jarn.com/public

to your buildout to get an updated version.

Setting up ejabberd (>=2.1.5)
-----------------------------

* Download the `ejabberd`_ installer
* We assume that your xmpp domain is ``myserver``. There should exist an administrator account ``admin@myserver``. In addition if you intend to run some of the tests in any of the ``jarn.xmpp.*`` packages you will need to be running an additional XMPP node on ``localhost``. You can safely remove any references to ``localhost`` if you are not interested in doing that.
* You will need two hosts (one if you are not running tests, see above).

  ::

  {hosts, ["myserver", "localhost"]}.

* Make sure you have enabled the `http_bind` module, as this is what the javascript clients will use to connect. You should have  something like this in your ejabberd.cfg:

  ::

    {5280, ejabberd_http, [
         http_bind,
         web_admin
         ]}

* Because ejabberd's implementation of XEP-0060 is not standard use of the ejabberd's ``dag`` module is necessary. So, make sure your pubsub module is configured appropriately:

  ::

    {mod_pubsub,   [
        {access_createnode, pubsub_createnode},
        {ignore_pep_from_offline, true},
        {last_item_cache, false},
        {nodetree, "dag"},
        {plugins, ["dag", "flat", "hometree", "pep"]}
        ]},

* In order to test and run custom XMPP components (for instance the collaborative editing component provided by ``jarn.xmpp.collaboration``) you will need to allow them to connect. This means you should have something similar to this configuration:

  ::

    {5347, ejabberd_service, [
              {access, all}, 
              {shaper_rule, fast},
              {ip, {127, 0, 0, 1}},
              {hosts,
               ["collaboration.myserver",
                "collaboration.localhost"],
               [{password, "secret"}]
              }
             ]},

The rest of the standard options should be fine. In any case a sample ``ejabberd.cfg`` is included in the `jarn.xmpp.buildout`_ package.

Test that you can access your ejabberd by logging to the admin interface (typically ``http://host:5280/admin``). You should also be able to access the ``http-bind`` interface at ``http://host:5280/http-bind``.

Setting up your front-end proxy
-------------------------------
On the client-side every authenticated user will be connected to your jabber server through an emulated bidirectional stream through HTTP. To allow for this you need a proxy in front of Plone that will be redirecting the XMPP stream to your XMPP server. It is possible to do without one using the inferior solution of Flash plugins but this is not going to be supported. 

So assuming you run ``nginx`` as a proxy at port ``80`` for the domain ``myserver``, Plone listens on ``8081`` and your ejabberd has the ``http_bind`` configured for port ``5280``, your ``nginx`` configuration will look like this:

    ::

        http {
            server {
                listen       80;
                server_name  myserver;

                location ~ ^/http-bind/ {
                    proxy_pass http://myserver:5280;
                }

                location / {
                    proxy_pass http://myserver:8081/VirtualHostBase/http/myserver:80/Plone/VirtualHostRoot/;
                }

            }
          }

Again, it might help you to have a look at the sample buildout provided in `jarn.xmpp.buildout`_.

Setting up your Plone instances
-------------------------------
Your instances will need to maintain a connection to the administrator account of your XMPP server. This is accomplished through ``Twisted`` and you will need to run a Twisted reactor on each of them. To do so include this in your instance section of your buildout:

  ::

    zcml-additional =
      <configure xmlns="http://namespaces.zope.org/zope">  
        <include package="jarn.xmpp.twisted" file="reactor.zcml" />
      </configure>

Again, use `jarn.xmpp.buildout`_ as a starting point!

Setting up a new Plone site
---------------------------
* Start ejabberd
* Start the Nginx frontend. ``sudo bin/frontend start``
* Start your zope instance.
* Access Zope via Nginx ``http://myserver/`` and create a new Plone site with ``jarn.xmpp.core``.
* Go to the Plone control panel, into the registry settings. Edit the jarn.xmpp.* settings to reflect your installation, passwords etc.
* Restart your Plone instance.
* Upon the first request the administrator will log to his account. You should see things happening in the logs and if there are any errors something might be wrong with your installation.
* Setup the the users and pubsub nodes. You do this by calling ``@@setup-xmpp`` like ``http://myserver/@@setup-xmpp``. The form will not report any errors as everything will happen asynchronously but you will get the results/failures on the console.

If you are going to use this on an existing site, you only need to perform the last step after making sure that your XMPP admin is connected.

Experimenting
=============

Setup
-----

* Add a few users.
* Add the *Online users* portlet.
* Add a *Pubsub node* portlet, where the node name is ``people`` and the type is ``collection``. This is the collective feed of all users.
* For each user you added add a *Pubsub node* portlet, where the node name is the user's id and the type is ``leaf``. This is the personal feed of the respective user.

Usage
-----

* Login several users in different browsers.
* On the *online users* portlet click on a user. This allows you to message him and he can start a chat session.
* Each user is able to post a message to his node. Others will receive in real time. The portlets will be updated on the next request.

Security
========

``jarn.xmpp.twisted`` includes an implementation of an authenticating client over BOSH according to `XEP-0206`_. This practically means that the javascript client never needs to know the password of the XMPP user. Instead, the user is authenticated directly between the XMPP server and the Plone instance. A pair of secret tokens are exchanged, valid for a short time (~2 minutes). It is this pair that is given to the javascript client and not the password.

When a user is created (either through the Plone interface or by running ``@@setup-xmpp`` for existing users), a random password is generated and stored internally in a persistent utility.

If you do not need to access the XMPP accounts outside of the Plone instance you can additionally hide the entire XMPP service behind a firewall and only allow connections to it from the Plone instances. This in combination with HTTPS should be enough for the paranoid among us.

Credits
=======

* Most of this work was done using the 10% time available to `Jarn AS`_ employees for the development of open-source projects.

.. _XEP-0071: http://xmpp.org/extensions/xep-0071.html
.. _XEP-0144: http://xmpp.org/extensions/xep-0144.html
.. _XEP-0060: http://xmpp.org/extensions/xep-0060.html
.. _XEP-0248: http://xmpp.org/extensions/xep-0248.html
.. _XEP-0133: http://xmpp.org/extensions/xep-0133.html
.. _XEP-0124: http://xmpp.org/extensions/xep-0124.html
.. _XEP-0206: http://xmpp.org/extensions/xep-0206.html
.. _ejabberd: http://www.ejabberd.im
.. _Jarn AS: http://jarn.com
.. _jarn.xmpp.buildout: http://github.com/ggozad/jarn.xmpp.buildout
.. _jarn.xmpp.twisted: http://pypi.python.org/pypi/jarn.xmpp.twisted
.. _jarn.xmpp.collaboration: http://pypi.python.org/pypi/jarn.xmpp.collaboration

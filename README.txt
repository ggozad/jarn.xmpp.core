Introduction
============

``jarn.xmpp.core`` provides the following basic functionality based on XMPP services:

* Integration of plone user accounts with XMPP accounts.
* Basic messaging and multi-user chat.
* A minimal microblogging environment based on XMPP PubSub.

It is part of a suite of packages aiming to provide XMPP services to Plone. The other two packages are

* `jarn.xmpp.twisted`_, provides XMPP-specific protocol implementation for twisted.
* `jarn.xmpp.collaboration`_ provides an XMPP protocol to do real-time collaborative editing as well as a Plone-targeted implementation.

Installation
============

Before setting up the package you need to have a working XMPP server and access to an administration account on the server. The package has only been tested with ejabberd version 2.1.5 and above which is recommended. In any case the following XMPP extensions need to be supported by the server you are going to use:

* `XEP-0071`_ XHTML-IM.
* `XEP-0144`_ Roster Item Exchange.
* `XEP-0060`_ Publish-Subscribe.
* `XEP-0248`_ PubSub Collection Nodes.
* `XEP-0133`_ Service Administration.

Setting up ejabberd (>=2.1.5)
-----------------------------

* Download `ejabberd`_ installer
* We assume that your xmpp domain is ``myserver``. There should exist an administrator account ``admin@myserver``. In addition if you intend to run tests you will need to be running an additional XMPP node on ``localhost``. You can safely remove any references to ``localhost`` if you do not want to do that.
* You will need two hosts (one if you are not running tests, see above).

  ::

  {hosts, ["myserver", "localhost"]}.

* Make sure you have enabled the `http_bind` module, as this is what the javascript clients will use to connect. You should have  something like this in your ejabberd.cfg:

  ::

    {5280, ejabberd_http, [
         http_bind,
         web_admin
         ]}

* Because ejabberd's implementation of XEP-0060 is not standard use of the ``dag`` module is necessary. So, make sure your pubsub module is configured appropriately:

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

Setting up a new Plone site
---------------------------
* Start ejabberd
* Start the Nginx frontend. ``sudo bin/frontend start``
* Start your zope instance.
* Access Zope via Nginx ``http://myserver/`` and create a new Plone site with ``jarn.xmpp.core``.
* Go to the Plone control panel, into the registry settings. Edit the jarn.xmpp.* settings to reflect your installation, passwords etc.
* Upon the first request the administrator will log to his account. You should see things happening in the logs and if there are any errors something might be wrong with your installation.
* Setup the the users and pubsub nodes. You do this by calling ``@@setup-xmpp`` like ``http://myserver/@@setup-xmpp``. The form will not report any errors as everything will happen asynchronously but you will get the results/failures on the console.

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

* Login several users in different browsers. Note the ugly logs at the bottom with the XMPP stanzas exchanged.
* On the *online users* portlet click on a user. This allows you to message him and he can start a chat session.
* Each user is able to post a message to his node. Others will receive in real time. The portlets will be updated on the next request.

.. _XEP-0071: http://xmpp.org/extensions/xep-0071.html
.. _XEP-0144: http://xmpp.org/extensions/xep-0144.html
.. _XEP-0060: http://xmpp.org/extensions/xep-0060.html
.. _XEP-0248: http://xmpp.org/extensions/xep-0248.html
.. _XEP-0133: http://xmpp.org/extensions/xep-0133.html
.. _ejabberd: http://www.ejabberd.im

Credits
=======

* Most of this work was done using the 10% time available to `Jarn AS`_ employees for the development of open-source projects.

.. _Jarn AS: http://jarn.com
.. _jarn.xmpp.buildout: http://github.com/ggozad/jarn.xmpp.buildout
.. _jarn.xmpp.twisted: http://pypi.python.org/pypi/jarn.xmpp.twisted
.. _jarn.xmpp.collaboration: http://pypi.python.org/pypi/jarn.xmpp.collaboration

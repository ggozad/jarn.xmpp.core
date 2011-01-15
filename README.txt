Introduction
============

Installation
============

Before setting up the package you need to have a working XMPP server and access to an administration account on the server. The package has only been tested with ejabberd version 2.1.5 and above so far which is recommended. In any case the following XMPP extensions need to be supported by the server you are going to use:

* `XEP-0071`_ XHTML-IM.
* `XEP-0144`_ Roster Item Exchange.
* `XEP-0060`_ Publish-Subscribe.
* `XEP-0248`_ PubSub Collection Nodes.
* `XEP-0133`_ Service Administration.

Setting up ejabberd (>=2.1.5)
-----------------------------

* Download `ejabberd`_
* Unless you decide to customize what the IXMPPSettings utility reports, as domain use ``localhost`` and the administrator should be ``admin@localhost`` with password ``admin``.
* Make sure you have enabled the `http_bind` module. You should have  something like this in your ejabberd.cfg:

  ::

    {5280, ejabberd_http, [
         captcha,
         http_bind,
         web_admin
         ]}

* Because ejabberd's implementation of XEP-0060 is not standard use of the ``dag`` module is necessary. So, make sure your pubsub module is configured appropriately:

  ::

    {mod_pubsub,   [ % requires mod_caps
        {access_createnode, pubsub_createnode},
        {ignore_pep_from_offline, true},
        {last_item_cache, false},
        {nodetree, "dag"},
        {plugins, ["dag", "flat", "hometree", "pep"]}
        ]},

The rest of the standard options should be fine. In any case a sample ``ejabberd.cfg`` is included in the buildout.

Test that you can access your ejabberd by logging to the admin interface (typically ``http://host:5280/admin``). You should also be able to access the ``http-bind`` interface at ``http://host:5280/http-bind``.

Setting up a new Plone site
---------------------------

* Start your zope instance. You can observe on the console that the reactor has started.
* Create a new Plone site and install ``plone.messaging.core``
* Before you add any users you need to setup the pubsub nodes. You do this by calling ``@@setup-xmpp``. Eventually this will take care of existing users as well but it's not there yet. The form will not report any errors as everything will happen asynchronously but you will get the result on the console.

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

* Login several users in different browsers. Note the ugly logs at the bottom with the XMPP stanzas exchanged. Each will be able to post a message to his node. Others will receive in real time. The portlets will be updated on reload.

* There exists an example of notification. This is intended as a demo and will change. In a folder make a few users reviewers and a few others contributors. When someone submits for publication all reviewers get a notification. When the document is published the owner gets a notification.

* From you normal jabber client login as one of the users. You will see that your contacts are online. Send them a messsage which will appear on their browser.

.. _XEP-0071: http://xmpp.org/extensions/xep-0071.html
.. _XEP-0144: http://xmpp.org/extensions/xep-0144.html
.. _XEP-0060: http://xmpp.org/extensions/xep-0060.html
.. _XEP-0248: http://xmpp.org/extensions/xep-0248.html
.. _XEP-0133: http://xmpp.org/extensions/xep-0133.html
.. _ejabberd: http://www.ejabberd.im

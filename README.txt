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


.. _XEP-0071: http://xmpp.org/extensions/xep-0071.html
.. _XEP-0144: http://xmpp.org/extensions/xep-0144.html
.. _XEP-0060: http://xmpp.org/extensions/xep-0060.html
.. _XEP-0248: http://xmpp.org/extensions/xep-0248.html
.. _XEP-0133: http://xmpp.org/extensions/xep-0133.html
.. _ejabberd: http://www.ejabberd.im

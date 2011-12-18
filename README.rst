============
Introduction
============

``jarn.xmpp.core`` is a Plone add-on providing the following functionality based on XMPP services:

* Integration of plone user accounts with XMPP accounts and authentication.
* A microblogging environment similar to twitter/yammer based on XMPP PubSub.
* Messaging.

It is part of a suite of packages aiming to provide XMPP services to Plone. The other two packages are

* `jarn.xmpp.twisted`_, provides XMPP-specific protocol implementation for twisted.
* `jarn.xmpp.collaboration`_ provides an XMPP protocol to do real-time collaborative editing as well as a Plone-targeted implementation.

============
Installation
============

Before setting up the package you need to have a working XMPP server and access to the administration account on the server. The package has only been tested with ejabberd version 2.1.5 and above which is recommended. In any case the following XMPP extensions need to be supported by the server you are going to use:

* `XEP-0071`_ XHTML-IM.
* `XEP-0054`_ vCard-temp.
* `XEP-0144`_ Roster Item Exchange.
* `XEP-0060`_ Publish-Subscribe.
* `XEP-0248`_ PubSub Collection Nodes.
* `XEP-0133`_ Service Administration.
* `XEP-0124`_ Bidirectional-streams Over Synchronous HTTP (BOSH)
* `XEP-0206`_ XMPP over BOSH
* `XEP-0049`_ Private XML Storage

--------
Buildout
--------
A sample buildout you can use as a starting point can be found at `jarn.xmpp.buildout`_.

-----------------------------
Setting up ejabberd (>=2.1.5)
-----------------------------

Automatic configuration
-----------------------
* Use the recipe provided in `jarn.xmpp.buildout`_ (in which case you will need to have erlang installed) or download the `ejabberd`_ installer.
* A minimal configuration for ejabberd can be generated for convenience by the ``ejabberd.cfg`` part of `jarn.xmpp.buildout`_. You will need to copy the ``templates`` directory and modify the recipe configuration accordingly::

    [ejabberd.cfg]
    recipe = collective.recipe.template
    input = templates/ejabberd.cfg.in
    output = ${buildout:directory}/etc/ejabberd.cfg
    xmppdomain = localhost
    admin_userid = admin
    collaboration_allowed_subnet = 0,0,0,0
    collaboration_port = 5347
    component_password = secret


where ``xmppdomain`` is the domain (or virtual host) running on your XMPP server and ``admin_userid`` is the id the the administrator account that Plone is going to use to interact with the server. The rest of the options are  used by ``jarn.xmpp.collaboration`` for the collaborative editing component connecting to the XMPP server. Here, ``collaboration_allowed_subnet`` specifies from which IPs the XMPP server is going to accept connections and should match the IPs your Plone instances are going to be using. Leaving it to ``0,0,0,0`` will allow all IPs, ``127,0,0,1`` will allow only ``localhost``. Finally ``collaboration_port`` is the port to which the collaboration component is going to connect to and ``component_password`` is the shared password between the component and the XMPP server.

Manual configuration
--------------------
If you already run an XMPP server here are some hints on how to set it up:

* We assume that your xmpp domain is ``localhost``. There should exist an administrator account ``admin@localhost``. In addition if you intend to run some of the tests in any of the ``jarn.xmpp.*`` packages you will need to be running an additional XMPP node on ``localhost`` if you use some other domain for production. You can safely remove any references to ``localhost`` if you are not interested in doing that.

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
        {plugins, ["dag", "flat", "hometree", "pep"]},
        {max_items_node, 1000}
        ]},

* In order to test and run custom XMPP components (for instance the collaborative editing component provided by ``jarn.xmpp.collaboration``) you will need to allow them to connect. This means you should have something similar to this configuration:

  ::

    {5347, ejabberd_service, [
              {access, all}, 
              {shaper_rule, fast},
              {ip, {127, 0, 0, 1}},
              {hosts,
               ["collaboration.localhost"],
               [{password, "secret"}]
              }
             ]},

The rest of the standard options should be fine.

Administrator account
---------------------
If you have not done so during installation you might need to create manually the administrator account. In the ejabberd folder execute::

    ./bin/ejabberdctl register admin localhost your_password

Test that you can access your ejabberd by logging to the admin interface (typically ``http://localhost:5280/admin``). You should also be able to access the ``http-bind`` interface at ``http://localhost:5280/http-bind``.

-------------------------------
Setting up your front-end proxy
-------------------------------
On the client-side every authenticated user will be connected to your jabber server through an emulated bidirectional stream through HTTP. To allow for this you need a proxy in front of Plone that will be redirecting the XMPP stream to your XMPP server. It is possible to do without one using the inferior solution of Flash plugins but this is not going to be supported. 

So assuming you run ``nginx`` as a proxy at port ``8080`` for the domain ``localhost``, Zope listens on ``8081``, there exists a Plone site with id  ``Plone`` and your ejabberd has the ``http_bind`` configured for port ``5280``, your ``nginx`` configuration will look like this:

    ::

        http {
            server {
                listen       8080;
                server_name  localhost;
                location ~ ^/http-bind/ {
                    proxy_pass http://localhost:5280;
                }

                location / {
                    proxy_pass http://localhost:8081/VirtualHostBase/http/localhost:8080/Plone/VirtualHostRoot/;
                }
            }
          }

-------------------------------
Setting up your Plone instances
-------------------------------
Your instances will need to maintain a connection to the administrator account of your XMPP server. This is accomplished through ``Twisted`` and you will need to run a Twisted reactor on each of them. To do so include this in your instance section of your buildout:

  ::

    zcml-additional =
      <configure xmlns="http://namespaces.zope.org/zope">  
        <include package="jarn.xmpp.twisted" file="reactor.zcml" />
      </configure>

Again, it will help you to have a look at the sample buildout provided in `jarn.xmpp.buildout`_.

---------------------------
Setting up a new Plone site
---------------------------
* Start ejabberd (if you used the recipe to build ejabberd, ``bin/ejabberd`` will do the job).
* Start the Nginx frontend. ``bin/frontend start``
* Start your zope instance.
* Access Zope directly at ``http://localhost:8081/manage`` and create a new Plone site with ``jarn.xmpp.core`` (or ``jarn.xmpp.collaboration`` if you want that package installed as well).
* Go to the Plone control panel, into the registry settings. Edit the jarn.xmpp.* settings to reflect your installation, passwords etc.
* Restart your Plone instance.
* Upon the first request the administrator will log to his account. You should see things happening in the logs and if there are any errors something might be wrong with your installation.
* Setup the users and pubsub nodes. You do this by calling ``@@setup-xmpp`` like ``http://localhost:8080/@@setup-xmpp``. The form will not report any errors as everything will happen asynchronously but you will get the results/failures on the console.

If you are going to use this on an existing site, you only need to perform the last step after making sure that your XMPP admin is connected.

--------------------------
Making sure things work ;)
--------------------------

This is a complex infrastructure so it can be hard to know what goes wrong sometimes. Do not despair, here are a few things to try:

* Make sure your ejabberd is running. Connect to it normal client as the admin user.
* Verify that http-binding is setup properly on ejabberd. Visiting ``http://localhost:5280/http-bind`` should tell you it's working.
* Verify that XMPP requests will get properly through your proxy. Visiting ``http://localhost:8080/http-bind/`` should give you the same result as above.
* When you start your Zope instance in foreground you can verify the Twisted reactor is running fine:

  ::

    2011-09-01 14:37:38 INFO jarn.xmpp.twisted Starting Twisted reactor...
    2011-09-01 14:37:38 INFO jarn.xmpp.twisted Twisted reactor started
    2011-09-01 14:37:38 INFO Zope Ready to handle requests

* After the first request to the site, you should also see in the logs:

  ::

    2011-09-01 14:45:48 INFO jarn.xmpp.core XMPP admin client has authenticated succesfully.

* After having run ``@@setup-xmpp``, logging-in to the Plone site with a user should also authenticate him with the XMPP server. This is indicated in the logs by:

  ::

    2011-09-01 14:45:50 INFO jarn.xmpp.core Pre-binded ggozad@localhost/auto-QravOoyEeE

=============
Experimenting
=============

-------------
Usage
-------------

* Add a few users.
* Login as one of them, and in a different browser as some other. Use the frontend to access the site, if you used the settings above this should be ``http://localhost:8080``.
* All actions are performed through the viewlet on the top right: ``Online users`` will display the users currently logged in. Clicking it will give you the list of users. You can message them directly or look at their personal feed.
* Try posting an entry to your feed. Links will be transformed automatically. As soon as you submit other logged-in users will receive a notification in real-time. Using a recent browser that supports geolocation will allow you also share your location at the time of the post.
* Try commenting on a feed post.
* By clicking on the "Following" user action you can select which users you want to follow, or follow them all.
* You can see all posts by clicking on ``Site feed`` on the viewlet.

========
Security
========

``jarn.xmpp.twisted`` includes an implementation of an authenticating client over BOSH according to `XEP-0206`_. This practically means that the javascript client never needs to know the password of the XMPP user. Instead, the user is authenticated directly between the XMPP server and the Plone instance. A pair of secret tokens are exchanged, valid for a short time (~2 minutes). It is this pair that is given to the javascript client and not the password.

When a user is created (either through the Plone interface or by running ``@@setup-xmpp`` for existing users), a random password is generated and stored internally in a persistent utility.

If you do not need to access the XMPP accounts outside of the Plone instance you can additionally hide the entire XMPP service behind a firewall and only allow connections to it from the Plone instances. This in combination with HTTPS should be enough for the paranoid among us.

=======
Testing
=======

Some of the included tests are functional tests that require a XMPP server running on ``localhost`` as well as an administrator account setup up on this server with JID ``admin@localhost`` and password ``admin``. If you wish to run those you have to specify a *level* 2 on your testrunner, i.e.

    ::

    ./bin/test -a 2 -s jarn.xmpp.core

=======
Credits
=======

* The UI was designed and implemented by Denys Mishunov.
* Most of this work was done using the 10% time available to `Jarn AS`_ employees for the development of open-source projects.

.. _XEP-0071: http://xmpp.org/extensions/xep-0071.html
.. _XEP-0054: http://xmpp.org/extensions/xep-0054.html
.. _XEP-0144: http://xmpp.org/extensions/xep-0144.html
.. _XEP-0060: http://xmpp.org/extensions/xep-0060.html
.. _XEP-0248: http://xmpp.org/extensions/xep-0248.html
.. _XEP-0133: http://xmpp.org/extensions/xep-0133.html
.. _XEP-0124: http://xmpp.org/extensions/xep-0124.html
.. _XEP-0206: http://xmpp.org/extensions/xep-0206.html
.. _XEP-0049: http://xmpp.org/extensions/xep-0049.html
.. _ejabberd: http://www.ejabberd.im
.. _Jarn AS: http://jarn.com
.. _jarn.xmpp.buildout: http://github.com/ggozad/jarn.xmpp.buildout
.. _jarn.xmpp.twisted: http://pypi.python.org/pypi/jarn.xmpp.twisted
.. _jarn.xmpp.collaboration: http://pypi.python.org/pypi/jarn.xmpp.collaboration

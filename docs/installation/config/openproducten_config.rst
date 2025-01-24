.. _installation_configuration:

===============================
Open Producten configuration (admin)
===============================

Before you can work with Open Producten after installation, a few settings need to be
configured first.

.. note::

    This document describes the manual configuration via the admin.

.. _installation_configuration_sites:

Setting the domain
==================

In the admin, under **Configuratie > Websites**, make sure to change the existing
``Site`` to the domain under which Open Producten will be deployed (see
:ref:`the manual<manual_configuration>` for more information).

.. note:: Due to a cache-bug in the underlying framework, you need to restart all
   replicas for this change to take effect everywhere.

.. _installation_configuration_notificaties_api:

Create an API token
===================

Open Producten
---------
By creating an API token, we can perform an API test call to verify the successful
installation.

Navigate to **Users** > **Token** and click on **Token toevoegen**
in the top right.

1. Select the user you want to create a token for
2. Click **Opslaan** in the bottom left

After creating the **Token** the **key** is shown in the list page. This value
can be used in the ``Authorization`` header.


Making an API call
==================

Open Producten
---------
We can now make an HTTP request to one of the APIs of Open Producten. For this
example, we have used `curl`_ to make the request.

.. code-block:: bash

   curl --request GET \
   --header 'Authorization: Token 1d4df96cfe14543558118805c5e9252629e805a0' \
   --header 'Content-Type: application/json' \
   {{base_url}}/producten/api/v1/producten

The example above uses the same value configured in
:ref:`installation_configuration_sites`.

.. _Curl: https://curl.se/docs/manpage.html

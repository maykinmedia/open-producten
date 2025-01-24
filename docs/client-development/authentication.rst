.. _client-development-auth:

Authentication and authorization
================================

Open Producten uses the described authentication and authorization mechanism based on
API tokens. It does not implement its own mechanism but uses `TokenAuthentication`_
provided by `Django REST Framework`_.

To connect to Open Producten, you have received a token key which should be included
in your request's HTTP headers:

.. code-block:: none

   Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b


.. _TokenAuthentication: https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication
.. _Django REST Framework: https://www.django-rest-framework.org/

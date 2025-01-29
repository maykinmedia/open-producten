.. _installation_prerequisites:

Prerequisites
=============

While the `container images <https://hub.docker.com/r/maykinmedia/open-producten/>`_
contain all the necessary dependencies, Open Producten does require extra service to
deploy the full stack. These dependencies and their supported versions are
documented here.

The ``docker-compose.yml`` (not suitable for production usage!) in the root of the
repository also describes these dependencies.

Redis
-----

Open Producten uses Redis as a cache backend and especially relevant for admin sessions.

Supported versions: 5, 6, 7.

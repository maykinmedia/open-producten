Architecture
============

The overall architecture remains faithful to the `Common Ground`_ principles
and all API specifications where applicable.

The architecture of **Open Producten** focusses on excellent performance, optimal
stability and to guarantee data integrity.

To that end, **Open Producten** combines the Producttype API and Producten API that
are essentially tightly coupled, into a single product. This allows for major
performance improvements since related objects (like a `ProductType` for a `Product`)
do not need to fetched over the network but can be directly obtained from the
database. This also guarantees data integrity on database level, rather than on
service (API) level.

In addition, **Open Producten** uses caching wherever possible to prevent needless
requests over the netwerk to fetch data from external API's. Data integrity can
not be guaranteed on database level when relations are created to external
API's. In this case, data integrity is enforced on service level as much as
possible.

No permanent copies are made of original sources in **Open Producten** as dictated
by the `Common Ground`_ principles.

Overview
--------

.. _Common Ground: https://commonground.nl/

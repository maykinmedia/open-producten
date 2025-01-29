.. _development_principles:

Principles and code style (draft)
=================================

Defining (architectural) principles and code style keeps the code base consistent
and manages expectations for contributions.

Backend
-------

On the backend, we use the `Django framework`_ and follow the project structure
of having apps within the project.

- Django apps contains models, views and API definitions. They group a logical part of
  the greater project which is loosely coupled to other apps.

  Tests are in the django app package. Split tests in logical modules, and try to avoid
  complex nesting structures.

- All apps must go in the ``src/open_producten`` directory, which namespaces all the Open Producten
  code in the ``open_producten`` package. This prevents name conflicts with third party
  applications.

- Application names should always be in plural form.

- Settings go in ``open_producten.conf``, which is split according to deploy environment:

      - dev
      - ci
      - staging
      - production
      - docker

  Settings must always be defined in the ``open_producten.conf.base`` with sane defaults.

- Global runtime Open Producten configuration (database backed) should go in the
  ``open_producten.config`` app.

- Generic tools that are used by specific apps should be a ``open_producten`` sub-package,
  or possibly go in ``open_producten.utils``.

- Integration with other, third-party services/interfaces should go in a
  ``open_producten.contrib`` package. This is currently (!) not the case yet.

- Code style is enforced in CI with `black`_. When Black is not conclusive, stick to
  `PEP 8`_.

- Imports are sorted using isort_.

.. _Django framework: https://www.djangoproject.com/
.. _black: https://github.com/psf/black
.. _PEP 8: https://www.python.org/dev/peps/pep-0008/
.. _isort: https://pycqa.github.io/isort/

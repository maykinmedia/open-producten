Security measures in Open Producten
===================================

The following is a non-exhaustive list of configurations in Open Producten to enhance
security.

Nginx template considerations
-----------------------------

When deploying Open Producten on a VM, nginx is used as a reverse proxy. A number of headers
are set in the virtual host:

``Referrer-Policy: "same-origin";``
    the ``HTTP_REFERER`` header is sent only to Open Producten pages

``X-XSS-Protection: "1; mode=block";``
    note that this is not honored by most browsers anymore, but it doesn't hurt to
    include it

``Content-Security-Policy``
    opt-in, configure the deployment playbook accordingly

``Feature-Policy: "autoplay 'none'; camera 'none'" always;``
    there's no need for these :-)

Open Producten settings
-----------------------

``X-Frame-Options`` is set to ``DENY``
    no (i)frames are allowed at all

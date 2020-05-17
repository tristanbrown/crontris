========
Crontris
========
A scheduler microservice.

Install
=======

Coming soon

Build
=====

After each stage of development:
- git commit the changes.
- Use the Makefile to update the docker image.
- ``make build push``
- On the host, ``docker pull`` the new image and respawn the container.

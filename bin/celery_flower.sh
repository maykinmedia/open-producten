#!/bin/bash
exec celery --workdir src --app open_producten flower

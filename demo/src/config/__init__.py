# -*- coding: utf-8 -*-
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ.setdefault('DJANGO_CONFIGURATION', 'Local')
from configurations import importer

importer.install(check_options=True)

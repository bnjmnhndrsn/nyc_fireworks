# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Firework(models.Model):
    location = models.CharField(max_length=200)
    sponsor = models.CharField(max_length=200)
    event_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

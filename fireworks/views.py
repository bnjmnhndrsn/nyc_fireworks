# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from django.http import HttpResponse
from .models import Firework

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

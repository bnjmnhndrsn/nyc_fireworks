# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from django.http import HttpResponse
from .models import Firework
from .serializers import encode_firework

def index(request):
    fireworks = Firework.objects.all()
    serialized = [encode_firework(firework) for firework in fireworks]
    return HttpResponse(json.dumps(serialized))

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from django.http import HttpResponse
from django.utils import timezone

from .models import Firework
from .serializers import encode_firework

def index(request):
    now = timezone.now()
    upcoming_fireworks = Firework.objects.filter(event_at__gte=now, cancelled=False)
    serialized = [encode_firework(firework) for firework in upcoming_fireworks]
    return HttpResponse(json.dumps(serialized))

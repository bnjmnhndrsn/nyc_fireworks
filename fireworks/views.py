# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from django.http import HttpResponse
from django.utils import timezone

from .models import Firework
from .serializers import encode_firework
from .tasks import do_nothing

def index(request):
    now = timezone.now()
    upcoming_fireworks = Firework.objects.filter(event_at__gte=now, cancelled=False)
    serialized = [encode_firework(firework) for firework in upcoming_fireworks]
    do_nothing.delay()
    return HttpResponse(json.dumps(serialized))

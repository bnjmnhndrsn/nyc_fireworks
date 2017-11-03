# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytz

from django.db import models
from django.utils import timezone

eastern = pytz.timezone('US/Eastern')

class Firework(models.Model):
    location = models.CharField(max_length=200)
    sponsor = models.CharField(max_length=200)
    event_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled = models.BooleanField(default=False)

    def __unicode__(self):
        return '%s at %s' % (self.location, self.event_at.isoformat())
        
    def get_new_tweet_text(self):
        return 'New fireworks! %s on %s' % (
            self.location, timezone.localtime(self.event_at).strftime('%b %d at %I:%M %p')
        )
    
    def get_cancelled_tweet_text(self):
        return 'Cancelled! No fireworks at %s on %s' % (
            self.location, timezone.localtime(self.event_at).strftime('%b %d at %I:%M %p')
        )
    
    def get_update_tweet_text(self):
        days = (self.event_at - timezone.now()).days
        localized_time = timezone.localtime(self.event_at)
        
        if days == 14:
            prefix = 'Fireworks in 2 weeks!' 
            strftime_format = 'on %b %d at %I:%M %p'
        elif days == 7:
            prefix = 'Fireworks in 1 week!' 
            strftime_format = 'on %b %d at %I:%M %p'
        elif days == 0:
            prefix = 'Fireworks today!'
            strftime_format = 'at %I:%M %p'
        elif days == 1:
            prefix = 'Fireworks tomorrow!'
            strftime_format = 'at %I:%M %p'
        else: 
            prefix = localized_time.strftime('Fireworks on %A!')
            strftime_format = 'at %I:%M %p'
            
        return '%s %s %s' % (
            prefix, self.location, localized_time.strftime(strftime_format)
        )
        
        
        
        

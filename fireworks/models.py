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
        timezone.activate(eastern)
        text = 'New 🎆 announced! %s on %s sponsored by %s' % (
            self.location, timezone.localtime(self.event_at).strftime('%b %d at %I:%M %p'), self.sponsor
        )
        timezone.deactivate()
        return text
    
    def get_cancelled_tweet_text(self):
        timezone.activate(eastern)
        text = 'Cancelled! No 🎆  at %s on %s' % (
            self.location, timezone.localtime(self.event_at).strftime('%b %d at %I:%M %p')
        )
        timezone.deactivate()
        return text
    
    def get_morning_reminder_tweet_text(self, days):
        timezone.activate(eastern)
        localized_time = timezone.localtime(self.event_at)
        
        if days == 14:
            prefix = '🎆 in 2 weeks!' 
            strftime_format = 'on %b %d at %I:%M %p'
        elif days == 7:
            prefix = '🎆 in 1 week!' 
            strftime_format = 'on %b %d at %I:%M %p'
        elif days == 0:
            prefix = '🎆 today!'
            strftime_format = 'at %I:%M %p'
        elif days == 1:
            prefix = '🎆 tomorrow!'
            strftime_format = 'at %I:%M %p'
        else: 
            prefix = localized_time.strftime('Fireworks %A!')
            strftime_format = 'at %I:%M %p'
            
        text = '%s %s %s, sponsored by %s' % (
            prefix, self.location, localized_time.strftime(strftime_format), self.sponsor
        )
        timezone.deactivate()
        return text
    
    def get_one_hour_reminder_text(self):
        timezone.activate(eastern)
        localized_time = timezone.localtime(self.event_at)
        return '🎆 in one hour! %s, sponsored by %s' % (
            self.location, self.sponsor
        )
        
    def get_now_reminder_text(self):
        timezone.activate(eastern)
        localized_time = timezone.localtime(self.event_at)
        return '🎆 starting now! %s, sponsored by %s' % (
            self.location, self.sponsor
        )
        
        
        
        

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import mock
from freezegun import freeze_time
from datetime import datetime
import pytz

from django.test import TestCase
from django.core.management import call_command
from django.utils.six import StringIO
from django.utils import timezone

from fireworks.models import Firework

eastern = pytz.timezone('US/Eastern')


sample_1 = '''
<html>
<body>
<div class="richtext">The following is a list of legal fireworks displays that have been issued permits by the Fire Department:
<div><br></div>
<div>Saturday, October 14, 2017, 10:30 PM&nbsp;</div>
<div>Barge Off Governors Island&nbsp;</div>
<div>Sponsor: Prodject&nbsp;</div>
<div><br></div>
<div>Wednesday, October 25, 2017, 9:15 PM</div>
<div>Barge Off Ellis Island&nbsp;</div>
<div>Sponsor: Keller Williams Realty&nbsp;</div>
<div><br></div>
<div>Friday, November 3, 2017, 10:30 PM&nbsp;</div>
<div>Central Park Cherry Hill&nbsp;</div>
<div>Sponsor: NY Road Runners&nbsp;</div>
<div><br></div>
<div>Wednesday, December 5, 2017, 8:35 PM&nbsp;</div>
<div>St. John's University - Great Lawn&nbsp;</div>
<div>Sponsor: St. John's University</div>
<div style="position: absolute; left: 0px; top: -25px; width: 1px; height: 1px; overflow: hidden;" data-mce-bogus="1" class="mcePaste" id="_mcePaste"></div><!-- start ct -->&nbsp;</div>
</body>
</html>
'''

sample_2 = '''
<html>
<body>
<div class="richtext">The following is a list of legal fireworks displays that have been issued permits by the Fire Department:
<div><br></div>
<div>Friday, November 3, 2017, 10:30 PM&nbsp;</div>
<div>Central Park Cherry Hill&nbsp;</div>
<div>Sponsor: NY Road Runners&nbsp;</div>
<div><br></div>
<div>Wednesday, December 5, 2017, 8:35 PM&nbsp;</div>
<div>St. John's University - Great Lawn&nbsp;</div>
<div>Sponsor: St. John's University</div>
<div><br></div>
<div>Wednesday, December 12, 2017, 8:00 PM&nbsp;</div>
<div>Prospect Park - Great Meadow&nbsp;</div>
<div>Sponsor: Wayne Industries</div>
<div style="position: absolute; left: 0px; top: -25px; width: 1px; height: 1px; overflow: hidden;" data-mce-bogus="1" class="mcePaste" id="_mcePaste"></div><!-- start ct -->&nbsp;</div>
</body>
</html>
'''

malformed_sample = '''
<html>
<body>
<div class="richtext">The following is a list of legal fireworks displays that have been issued permits by the Fire Department:
<div><br></div>
<div>Friday, November 3, 2017, 10:30 PM&nbsp;</div>
<div><br></div>
<div>Wednesday, December 5, 2017, 8:35 PM&nbsp;</div>
<div>Sponsor: St. John's University</div>
<div><br></div>
<div>Wednesday, December 12, 2017, 8:00 PM&nbsp;</div>
<div style="position: absolute; left: 0px; top: -25px; width: 1px; height: 1px; overflow: hidden;" data-mce-bogus="1" class="mcePaste" id="_mcePaste"></div><!-- start ct -->&nbsp;</div>
</body>
</html>
'''

class LoadFireworksTestCase(TestCase):
    @freeze_time("2017-10-15 03:04:31", tz_offset=-4)
    @mock.patch('fireworks.management.commands.load_fireworks.get_request_text')
    def test_load_fireworks_creates_firework_for_each_new_upcoming_event(self, get_request_text_mock):
        out = StringIO()
        get_request_text_mock.return_value = sample_1
        call_command('load_fireworks', stdout=out)
        self.assertEqual(Firework.objects.count(), 3)

        fireworks = Firework.objects.all().order_by('event_at')
        self.assertEqual(fireworks[0].location, 'Barge Off Ellis Island')
        self.assertEqual(fireworks[0].event_at, eastern.localize(datetime(2017, 10, 25, 21, 15)))
        self.assertEqual(fireworks[1].location, 'Central Park Cherry Hill')
        self.assertEqual(fireworks[1].event_at, eastern.localize(datetime(2017, 11, 3, 22, 30)))
        self.assertEqual(fireworks[2].location, 'St. John\'s University - Great Lawn')
        self.assertEqual(fireworks[2].event_at, eastern.localize(datetime(2017, 12, 5, 20, 35)))

    @freeze_time("2017-10-15 03:04:31", tz_offset=-4)
    @mock.patch('fireworks.management.commands.load_fireworks.get_request_text')
    def test_load_fireworks_updates_fireworks(self, get_request_text_mock):
        out = StringIO()
        get_request_text_mock.return_value = sample_1
        call_command('load_fireworks', stdout=out)
        self.assertEqual(Firework.objects.count(), 3)

        get_request_text_mock.return_value = sample_2
        call_command('load_fireworks', stdout=out)
        self.assertEqual(Firework.objects.count(), 4)

        fireworks = Firework.objects.all().order_by('event_at')
        self.assertEqual(fireworks[0].location, 'Barge Off Ellis Island')
        self.assertTrue(fireworks[0].cancelled)
        self.assertEqual(fireworks[1].location, 'Central Park Cherry Hill')
        self.assertFalse(fireworks[1].cancelled)
        self.assertEqual(fireworks[2].location, 'St. John\'s University - Great Lawn')
        self.assertFalse(fireworks[2].cancelled)
        self.assertEqual(fireworks[3].location, 'Prospect Park - Great Meadow')
        self.assertFalse(fireworks[2].cancelled)

    @mock.patch('fireworks.management.commands.load_fireworks.get_request_text')
    def test_does_not_cancel_fireworks_if_theyve_already_happened(self, get_request_text_mock):
        out = StringIO()
        get_request_text_mock.return_value = sample_1
        with freeze_time("2017-10-15 03:04:31", tz_offset=-4):
            call_command('load_fireworks', stdout=out)
        self.assertEqual(Firework.objects.count(), 3)

        get_request_text_mock.return_value = sample_2
        with freeze_time("2017-10-26 03:04:31", tz_offset=-4):
            call_command('load_fireworks', stdout=out)
        self.assertEqual(Firework.objects.count(), 4)

        fireworks = Firework.objects.all().order_by('event_at')
        self.assertEqual(fireworks[0].location, 'Barge Off Ellis Island')
        self.assertFalse(fireworks[0].cancelled)

    @mock.patch('fireworks.management.commands.load_fireworks.get_request_text')
    def test_raises_error_if_can_find_node_with_data(self, get_request_text_mock):
        out = StringIO()
        get_request_text_mock.return_value = '<div></div>'
        with self.assertRaises(RuntimeError):
            call_command('load_fireworks', stdout=out)

    @mock.patch('fireworks.management.commands.load_fireworks.get_request_text')
    def test_raises_error_if_node_with_data_doesnt_parse_to_expected_form(self, get_request_text_mock):
        out = StringIO()
        get_request_text_mock.return_value = malformed_sample
        with self.assertRaises(RuntimeError):
            call_command('load_fireworks', stdout=out)

class TweetUpdatesTestCase(TestCase):
    @mock.patch('fireworks.management.commands.tweet_updates.tweet')
    def test_sends_updates_for_any_fireworks_created_within_last_24_hours(self, tweet_mock):
        out = StringIO()
        with freeze_time("2017-10-15 03:04:31", tz_offset=-4):
            yesterday_tweet = Firework.objects.create(
                event_at=eastern.localize(datetime(2017, 11, 25, 21, 15)),
                location='',
                sponsor=''
            )
        
        with freeze_time("2017-10-16 03:04:31", tz_offset=-4):
            today_tweet = Firework.objects.create(
                event_at=eastern.localize(datetime(2017, 11, 25, 21, 15)),
                location='Location',
                sponsor='Sponsor'
            )
        
        with freeze_time("2017-10-16 04:04:31", tz_offset=-4):
            call_command('tweet_updates', stdout=out)
            calls = [mock.call(today_tweet.get_new_tweet_text())]
            tweet_mock.assert_has_calls(calls)
        
    
    @mock.patch('fireworks.management.commands.tweet_updates.tweet')
    def test_sends_updates_for_tweets_cancelled_with_last_24_hours(self, tweet_mock):
        out = StringIO()
        with freeze_time("2017-10-15 03:04:31", tz_offset=-4):
            cancelled_yesterday = Firework.objects.create(
                event_at=eastern.localize(datetime(2017, 11, 23, 21, 15)),
                location='',
                sponsor=''
            )
        
        with freeze_time("2017-10-16 03:04:31", tz_offset=-4):
            cancelled_today = Firework.objects.create(
                event_at=eastern.localize(datetime(2017, 11, 25, 21, 15)),
                location='Location',
                sponsor='Sponsor'
            )
        
        with freeze_time("2017-10-17 03:04:31", tz_offset=-4):
            cancelled_yesterday.cancelled = True
            cancelled_yesterday.save()
        
        with freeze_time("2017-10-18 03:04:31", tz_offset=-4):
            cancelled_today.cancelled = True
            cancelled_today.save()
        
        with freeze_time("2017-10-18 04:04:31", tz_offset=-4):
            call_command('tweet_updates', stdout=out)
            calls = [mock.call(cancelled_today.get_cancelled_tweet_text())]
            tweet_mock.assert_has_calls(calls)
        
        
            
    @mock.patch('fireworks.management.commands.tweet_updates.tweet')    
    def test_sends_updates_for_reminder_tweets(self, tweet_mock):
        out = StringIO()
        with freeze_time("2017-10-15 03:04:31", tz_offset=-4):
            two_weeks = Firework.objects.create(
                event_at=eastern.localize(datetime(2017, 10, 30, 21, 15)),
                location='Location 1',
                sponsor='Sponsor 1'
            )
            one_week = Firework.objects.create(
                event_at=eastern.localize(datetime(2017, 10, 23, 22, 15)),
                location='Location 2',
                sponsor='Sponsor 2'
            )
            three_days = Firework.objects.create(
                event_at=eastern.localize(datetime(2017, 10, 19, 23, 15)),
                location='Location 3',
                sponsor='Sponsor 3'
            )
            one_day = Firework.objects.create(
                event_at=eastern.localize(datetime(2017, 10, 17, 20, 15)),
                location='Location 4',
                sponsor='Sponsor 4'
            )
            today = Firework.objects.create(
                event_at=eastern.localize(datetime(2017, 10, 16, 21, 30)),
                location='Location 5',
                sponsor='Sponsor 5'
            )
            
        with freeze_time("2017-10-16 04:04:31", tz_offset=-4):
            call_command('tweet_updates', stdout=out)
            calls = [
                mock.call(today.get_reminder_tweet_text()),
                mock.call(one_day.get_reminder_tweet_text()),
                mock.call(three_days.get_reminder_tweet_text()),
                mock.call(one_week.get_reminder_tweet_text()),
                mock.call(two_weeks.get_reminder_tweet_text())
            ]
            tweet_mock.assert_has_calls(calls)
            
    @mock.patch('fireworks.twitter.tweet')            
    def test_can_multiple_updates_at_same_time(self, tweet_mock):
        out = StringIO()
        with freeze_time("2017-10-15 03:04:31", tz_offset=-4):
            reminder = Firework.objects.create(
                event_at=eastern.localize(datetime(2017, 10, 30, 21, 15)),
                location='Location 1',
                sponsor='Sponsor 1'
            )
            cancelled = Firework.objects.create(
                event_at=eastern.localize(datetime(2017, 10, 30, 21, 15)),
                location='Location 2',
                sponsor='Sponsor 2'
            )
            
        with freeze_time("2017-10-16 04:04:31", tz_offset=-4):     
            cancelled.cancelled = True
            cancelled.save()       
            new_firework = Firework.objects.create(
                event_at=eastern.localize(datetime(2017, 10, 30, 21, 15)),
                location='Location 3',
                sponsor='Sponsor 3'
            )
            
            call_command('tweet_updates', stdout=out)
            
            calls = [
                mock.call(new_firework.get_new_tweet_text()),
                mock.call(cancelled.get_cancelled_tweet_text()),
                mock.call(reminder.get_reminder_tweet_text())
            ]
            timezone.deactivate()
            tweet_mock.assert_has_calls(calls)

        @freeze_time("2017-10-15 03:04:31", tz_offset=-4)
        @mock.patch('fireworks.twitter.tweet')            
        def test_trucates_long_content(self, tweet_mock):
            out = StringIO()
            firework = Firework.objects.create(
                event_at=eastern.localize(datetime(2017, 10, 30, 21, 15)),
                location='Location' * 100,
                sponsor='Sponsor 1'
            )
            call_command('tweet_updates', stdout=out)
            self.assertEqual(len(expect(contents.getvalue())), 142)

class FireworkModelTests(TestCase):
    def test_get_new_tweet_text(self):        
        with freeze_time("2017-10-16 03:04:31", tz_offset=-4):
            today_tweet = Firework.objects.create(
                event_at=eastern.localize(datetime(2017, 11, 25, 21, 15)),
                location='Location',
                sponsor='Sponsor'
            )
        
        with freeze_time("2017-10-16 04:04:31", tz_offset=-4):
            expected = 'New fireworks! Location on Nov 25 at 09:15 PM'
            self.assertEqual(today_tweet.get_new_tweet_text(), expected)
        
    
    def test_get_text_for_cancelled_fireworks(self):
        out = StringIO()        
        with freeze_time("2017-10-16 03:04:31", tz_offset=-4):
            cancelled_today = Firework.objects.create(
                event_at=eastern.localize(datetime(2017, 11, 25, 21, 15)),
                location='Location',
                sponsor='Sponsor'
            )
        
        with freeze_time("2017-10-18 03:04:31", tz_offset=-4):
            cancelled_today.cancelled = True
            cancelled_today.save()
        
        with freeze_time("2017-10-18 04:04:31", tz_offset=-4):
            expected = 'Cancelled! No fireworks at Location on Nov 25 at 09:15 PM'
            self.assertEqual(cancelled_today.get_cancelled_tweet_text(), expected)
        
        
            
    def test_get_text_for_reminder_tweets(self):
        with freeze_time("2017-10-15 03:04:31", tz_offset=-4):
            two_weeks = Firework.objects.create(
                event_at=eastern.localize(datetime(2017, 10, 30, 21, 15)),
                location='Location 1',
                sponsor='Sponsor 1'
            )
            one_week = Firework.objects.create(
                event_at=eastern.localize(datetime(2017, 10, 23, 22, 15)),
                location='Location 2',
                sponsor='Sponsor 2'
            )
            three_days = Firework.objects.create(
                event_at=eastern.localize(datetime(2017, 10, 19, 23, 15)),
                location='Location 3',
                sponsor='Sponsor 3'
            )
            one_day = Firework.objects.create(
                event_at=eastern.localize(datetime(2017, 10, 17, 20, 15)),
                location='Location 4',
                sponsor='Sponsor 4'
            )
            today = Firework.objects.create(
                event_at=eastern.localize(datetime(2017, 10, 16, 21, 30)),
                location='Location 5',
                sponsor='Sponsor 5'
            )
            
        with freeze_time("2017-10-16 04:04:31", tz_offset=-4):
            expected_today_text = 'Fireworks today! Location 5 at 09:30 PM'
            self.assertEqual(expected_today_text, today.get_reminder_tweet_text())
            
            expected_one_day_text = 'Fireworks tomorrow! Location 4 at 08:15 PM'
            self.assertEqual(expected_one_day_text, one_day.get_reminder_tweet_text())            
            
            expected_three_days_text = 'Fireworks Thursday! Location 3 at 11:15 PM'
            self.assertEqual(expected_three_days_text, three_days.get_reminder_tweet_text())
            
            expected_one_week_text = 'Fireworks in 1 week! Location 2 on Oct 23 at 10:15 PM'
            self.assertEqual(expected_one_week_text, one_week.get_reminder_tweet_text())
            
            expected_two_weeks_text = 'Fireworks in 2 weeks! Location 1 on Oct 30 at 09:15 PM'
            self.assertEqual(expected_two_weeks_text, two_weeks.get_reminder_tweet_text())
                        

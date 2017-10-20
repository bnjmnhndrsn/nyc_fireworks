# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import mock
from freezegun import freeze_time
from datetime import datetime
import pytz

from django.test import TestCase
from django.core.management import call_command
from django.utils.six import StringIO

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

class UserTestCase(TestCase):
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

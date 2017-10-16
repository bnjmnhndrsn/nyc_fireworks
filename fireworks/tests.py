# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import mock
from freezegun import freeze_time

from django.test import TestCase
from django.core.management import call_command
from django.utils.six import StringIO

from fireworks.models import Firework

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
<div><br></div>
<div>Wednesday, December 12, 2017, 8:00 PM&nbsp;</div>
<div>Prospect Park - Great Meadow&nbsp;</div>
<div>Sponsor: Wayne Industries</div>
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
        self.assertEqual(fireworks[1].location, 'Central Park Cherry Hill')
        self.assertEqual(fireworks[2].location, 'St. John\'s University - Great Lawn')
        
        

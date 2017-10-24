import tweepy

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from fireworks.models import Firework

eastern = pytz.timezone('US/Eastern')

TARGET_URL = 'http://www1.nyc.gov/nyc-resources/service/206/fireworks-displays'

# breaking this out into a seperate function to make testing easier
def get_request_text():
    r = requests.get(TARGET_URL)
    r.raise_for_status()
    return r.text

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def _log(self, text):
        if self.options['verbosity'] > 1:
            print text

    def get_text(self):
        text = get_request_text()
        soup = BeautifulSoup(text, 'html.parser')
        try:
            richtext_el_text = soup.find(class_="richtext").get_text()
        except AttributeError:
            raise RuntimeError('Cannot find DOM node containing fireworks info')

        return richtext_el_text

    def parse_text(self, text):
        rows = text.split('\n')[1:]
        rows = [row.strip() for row in rows if row.strip()]
        if len(rows) % 3 != 0:
            raise RuntimeError('Incorrect number of lines')

        result = []
        for i in range(0, len(rows) - 2, 3):
            result.append(self.parse_firework(*rows[i:i+3]))

        return result

    def parse_firework(self, date, location, sponsor):
        try:
            sponsor_name = re.search('Sponsor: (.+)', sponsor).group(1)
        except AttributeError:
            sponsor_name = ''

        return {
            'event_at': eastern.localize(parser.parse(date)),
            'location': location,
            'sponsor': sponsor_name
        }

    def create_or_update_fireworks(self, data):
        now = timezone.now()
        upcoming_fireworks = Firework.objects.filter(event_at__gte=now, cancelled=False)
        found_firework_ids = []
        for item in data:
            if item['event_at'] < now:
                continue

            try:
                found = upcoming_fireworks.get(**item)
                found_firework_ids.append(found.pk)
                self._log('found existing firework %s' % found)
            except Firework.DoesNotExist:
                firework = Firework(**item)
                self._log('creating new firework %s' % firework)
                if not self.options['dry_run']:
                    firework.save()
                    found_firework_ids.append(firework.pk)

        not_found_fireworks = upcoming_fireworks.exclude(id__in=found_firework_ids)
        if len(not_found_fireworks):
            not_found_string = '\n'.join([str(firework) for firework in not_found_fireworks])
            self._log('could not find fireworks:\n%s' % not_found_string)
            if not self.options['dry_run']:
                not_found_fireworks.update(cancelled=True)


    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Print scraped data instead of saving',
        )

    def handle(self, *args, **options):
        self.options = options
        text = self.get_text()
        parsed = self.parse_text(text)
        self.create_or_update_fireworks(parsed)

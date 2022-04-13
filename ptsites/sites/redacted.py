import datetime
import re

from ..schema.gazelle import Gazelle
from ..schema.site_base import Work, SignState
from ..utils.net_utils import NetUtils


class MainClass(Gazelle):
<<<<<<< HEAD:ptsites/sites/uhdbits.py
    URL = 'https://uhdbits.org/'
    USER_CLASSES = {
        'downloaded': [322122547200],
        'share_ratio': [2.0],
=======
    URL = 'https://redacted.ch/'
    USER_CLASSES = {
        'uploaded': [536870912000],
        'share_ratio': [0.65],
>>>>>>> upstream/master:ptsites/sites/redacted.py
        'days': [56]
    }

    def build_workflow(self, entry, config):
        return [
            Work(
                url='/',
                method='get',
<<<<<<< HEAD:ptsites/sites/uhdbits.py
                succeed_regex='<h1 class="hidden">UHDBits</h1>',
=======
                succeed_regex='<h1 class="hidden">Redacted</h1>',
>>>>>>> upstream/master:ptsites/sites/redacted.py
                check_state=('final', SignState.SUCCEED),
                is_base_content=True
            )
        ]

    def build_selector(self):
        selector = super(MainClass, self).build_selector()
        NetUtils.dict_merge(selector, {
            'detail_sources': {
                'default': {
<<<<<<< HEAD:ptsites/sites/uhdbits.py
                    'elements': {
                        'bar': 'ul#userinfo_stats',
                        'table': 'div.sidebar > div:nth-child(2) > ul'
                    }
=======
                    'elements': {'table': '#content > div > div.sidebar > div:nth-child(1) > ul'}
>>>>>>> upstream/master:ptsites/sites/redacted.py
                },
                'extend': {
                    'link': '/ajax.php?action=community_stats&userid={}'
                }
            },
            'details': {
                'join_date': {
<<<<<<< HEAD:ptsites/sites/uhdbits.py
                    'regex': 'Joined:\s+([^\n]+)',
=======
                    'regex': 'Joined: (.*?ago)',
>>>>>>> upstream/master:ptsites/sites/redacted.py
                    'handle': self.handle_join_date
                },
                'points': {
                    'regex': 'Bonus:\s+([\\d,.]+)',
                },
                'hr': None
            }
        })
        return selector

    def handle_join_date(self, value):
        year_regex = '(\\d+) years?'
        month_regex = '(\\d+) months?'
        week_regex = '(\\d+) weeks?'
        year = 0
        month = 0
        week = 0
        if year_match := re.search(year_regex, value):
            year = int(year_match.group(1))
        if month_match := re.search(month_regex, value):
            month = int(month_match.group(1))
        if week_match := re.search(week_regex, value):
            week = int(week_match.group(1))
        return (datetime.datetime.now() - datetime.timedelta(days=year * 365 + month * 31 + week * 7)).date()

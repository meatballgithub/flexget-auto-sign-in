import re

import requests

from ..base.sign_in import check_final_state, SignState, check_sign_in_state
from ..base.work import Work
from ..schema.nexusphp import NexusPHP
from ..utils import net_utils


class MainClass(NexusPHP):
    URL = 'https://tjupt.org/'
    IMG_REGEX = r'https://.*\.doubanio\.com/view/photo/s_ratio_poster/public/(p\d+)\.'
    ANSWER_REGEX = r"<input type='radio' name='answer' value='(.*?)'>(.*?)<br>"
    USER_CLASSES = {
        'uploaded': [5368709120000, 53687091200000],
        'days': [336, 924]
    }

    def sign_in_build_workflow(self, entry, config):
        return [
            Work(
                url='/attendance.php',
                method=self.sign_in_by_get,
                succeed_regex=['今日已签到'],
                assert_state=(check_sign_in_state, SignState.NO_SIGN_IN),
                is_base_content=True
            ),
            Work(
                url='/attendance.php',
                method=self.sign_in_by_douban,
                succeed_regex=['这是您的首次签到，本次签到获得.*?个魔力值。',
                               '签到成功，这是您的第.*?次签到，已连续签到.*?天，本次签到获得.*?个魔力值。'],
                assert_state=(check_final_state, SignState.SUCCEED)
            )
        ]

    @property
    def details_selector(self) -> dict:
        selector = super().details_selector
        net_utils.dict_merge(selector, {
            'details': {
                'downloaded': None,
                'share_ratio': None,
                'seeding': {
                    'regex': '活动种子.*?(\\d+)'
                },
                'leeching': {
                    'regex': '活动种子.*?\\d+\\D+(\\d+)'
                },
                'hr': {
                    'regex': 'H&R.*?(\\d+)',
                    'handle': self.handle_hr
                }

            }
        })
        return selector

    def sign_in_by_douban(self, entry, config, work, last_content=None):
        img_name = re.search(self.IMG_REGEX, last_content).group(1)
        answers = re.findall(self.ANSWER_REGEX, last_content)
        answer = self.get_answer(config, img_name, answers)
        data = {
            'answer': answer,
            'submit': '提交'
        }
        print(data)
        # return self.request(entry, 'post', work.url, data=data)

    def get_answer(self, config, img_name, answers):
        for value, answer in answers:
            movies = requests.get(f'https://movie.douban.com/j/subject_suggest?q={answer}',
                                  headers={'user-agent': config.get('user-agent')}).json()
            for movie in movies:
                if img_name in movie.get('img'):
                    return value

    def handle_hr(self, hr):
        return str(100 - int(hr))

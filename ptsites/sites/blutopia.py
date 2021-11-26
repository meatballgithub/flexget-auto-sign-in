from ..schema.site_base import SignState, Work
from ..schema.unit3d import Unit3D


class MainClass(Unit3D):
    URL = 'https://blutopia.xyz/'
    USER_CLASSES = {
        'uploaded': [109951162777600],
        'days': [365]
    }

    def build_workflow(self, entry, config):
        return [
            Work(
                url='/',
                method='get',
                succeed_regex='<title>Blutopia - Where Quality Matters</title>',
                fail_regex=None,
                check_state=('final', SignState.SUCCEED),
                is_base_content=True
            )
        ]

    def build_selector(self):
        selector = super(MainClass, self).build_selector()
        return selector

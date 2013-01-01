import owebunit

class WolisTestCase(owebunit.WebTestCase):
    def __init__(self, *args, **kwargs):
        super(WolisTestCase, self).__init__(*args, **kwargs)
        self.config.host = 'http://func'

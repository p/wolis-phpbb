import owebunit
import os
import random
import xml.sax.saxutils

class WolisTestCase(owebunit.WebTestCase):
    def __init__(self, *args, **kwargs):
        super(WolisTestCase, self).__init__(*args, **kwargs)
        self.config.host = 'http://func'
        self.config.save_responses = True
        self.config.save_dir = '/var/www/func/responses'
        self.flavor = os.environ['FLAVOR']
        self._sid = None
    
    def login(self, username, password):
        params = {
            'username': username,
            'password': password,
            'login': 'Login',
        }
        
        self.post('/ucp.php?mode=login', body=params)
        self.assert_status(200)
        
        assert 'You have been successfully logged in.' in self.response.body
        
        self.find_sid()
    
    def acp_login(self, username, password):
        self.get_with_sid('/adm/index.php')
        self.assert_status(200)
        
        assert 'To administer the board you must re-authenticate yourself.' in self.response.body
        
        assert len(self.response.forms) == 2
        form = self.response.forms[1]
        
        doc = self.response.lxml_etree
        password_name = self.xpath_first(doc, '//input[@type="password"]').attrib['name']
        
        params = {
            'username': username,
            password_name: password,
        }
        
        params = owebunit.extend_params(form.params.list, params)
        self.post(form.computed_action, body=params)
        self.assert_status(200)
        
        assert 'You have successfully authenticated' in self.response.body
        
        self.find_sid()
    
    def find_sid(self):
        cookie_names = self._session._cookie_jar.keys()
        sid_name = None
        for name in cookie_names:
            if name.endswith('_sid'):
                if sid_name is None:
                    sid_name = name
                else:
                    raise ValueError, 'Duplicate sid cookies detected: %s and %s' % (sid_name, name)
        self._sid = self._session._cookie_jar[sid_name].value
    
    def apply_sid(self, url):
        if self._sid is None:
            raise ValueError, 'sid is not known - login first'
        # XXX quick and dirty
        if '?' in url:
            return url + '&sid=' + self._sid
        else:
            return url + '?sid=' + self._sid
        return url
    
    def get_with_sid(self, url):
        return self.get(self.apply_sid(url))
    
    def post_with_sid(self, url, **kwargs):
        return self.post(self.apply_sid(url), **kwargs)
    
    def link_href_by_text(self, text):
        doc = self.response.lxml_etree
        quoted_text = xml.sax.saxutils.quoteattr(text)
        # http://stackoverflow.com/questions/1999761/xpath-is-there-a-way-to-get-all-the-childrens-text-in-xpath
        link = self.xpath_first(doc, '//a[descendant-or-self::*/text()=%s]' % quoted_text)
        return link.attrib['href']
    
    def check_form_key_delay(self):
        '''Workaround for http://tracker.phpbb.com/browse/PHPBB3-11304.
        '''
        
        import time as _time
        import math
        
        # we don't need to wait a full second
        now = _time.time()
        wait = math.ceil(now) - now
        _time.sleep(wait)
    
    def random_suffix(self):
        return '-%d' % random.randint(1000, 9999)

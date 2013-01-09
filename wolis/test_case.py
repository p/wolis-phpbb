import owebunit
import owebunit.utils
import utu
import os
import os.path
import re
import random
import xml.sax.saxutils
from . import config

class WolisTestCase(utu.adjust_test_base(owebunit.WebTestCase)):
    def __init__(self, *args, **kwargs):
        super(WolisTestCase, self).__init__(*args, **kwargs)
        
        self.conf = config.Config()
        
        self.config.host = self.conf.test_url
        self.config.save_responses = True
        self.config.save_dir = self.conf.responses_dir
        self.flavor = os.environ['FLAVOR']
        self._sid = None
    
    def login(self, username, password):
        params = {
            'username': username,
            'password': password,
            'login': 'Login',
        }
        
        self.post('/ucp.php?mode=login', body=params)
        self.assert_successish()
        
        assert 'You have been successfully logged in.' in self.response.body
        
        self.find_sid()
    
    def acp_login(self, username, password):
        self.get_with_sid('/adm/index.php')
        self.assert_successish()
        
        assert 'To administer the board you must re-authenticate yourself.' in self.response.body
        
        assert len(self.response.forms) == 2
        form = self.response.forms[1]
        
        doc = self.response.lxml_etree
        password_name = owebunit.utils.xpath_first_check(doc, '//input[@type="password"]').attrib['name']
        
        params = {
            'username': username,
            password_name: password,
        }
        
        params = owebunit.extend_params(form.params.list, params)
        self.post(form.computed_action, body=params)
        self.assert_successish()
        
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
    
    def link_href_by_xpath(self, xpath):
        doc = self.response.lxml_etree
        link = owebunit.utils.xpath_first_check(doc, xpath)
        return link.attrib['href']
    
    def link_href_by_text(self, text):
        quoted_text = xml.sax.saxutils.quoteattr(text)
        # http://stackoverflow.com/questions/1999761/xpath-is-there-a-way-to-get-all-the-childrens-text-in-xpath
        xpath = '//a[descendant-or-self::*/text()=%s]' % quoted_text
        return self.link_href_by_xpath(xpath)
    
    def link_href_by_title(self, text):
        quoted_text = xml.sax.saxutils.quoteattr(text)
        xpath = '//a[@title=%s]' % quoted_text
        return self.link_href_by_xpath(xpath)
    
    def link_href_by_acp_tab_title(self, text):
        quoted_text = xml.sax.saxutils.quoteattr(text)
        xpath = '//div[@id="tabs"]//a[descendant-or-self::*/text()=%s]' % quoted_text
        return self.link_href_by_xpath(xpath)
    
    def clear_cache(self):
        import shutil
        cache_path = '/var/www/func/cache'
        for entry in os.listdir(cache_path):
            if not entry[0] == '.':
                path = os.path.join(cache_path, entry)
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.unlink(path)
    
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
    
    def assert_successish(self, session=None):
        if session is None:
            session = self
        
        session.assert_status(200)
        self.assert_no_php_spam(session)
        self.assert_no_phpbb_error(session)
    
    def assert_no_php_spam(self, session=None):
        if session is None:
            session = self
        
        assert 'Fatal error:' not in session.response.body
        assert 'phpBB Debug' not in session.response.body
        assert 'PHP Warning' not in session.response.body
        assert 'PHP Notice' not in session.response.body
        # xdebug php warning
        assert not re.search(r'Warning: .* in .* on line ', session.response.body)
    
    def assert_no_phpbb_error(self, session=None):
        '''Checks if the document appears to have a phpBB error in it.
        
        The check is somewhat fuzzy.
        '''
        
        if session is None:
            session = self
        
        doc = self.response.lxml_etree
        errorbox = owebunit.utils.xpath_first(doc, '//div[@class="errorbox"]')
        if errorbox is not None:
            severity = owebunit.utils.xpath_first_check(errorbox, './h3').text.strip()
            if severity != 'Warning':
                message_element = owebunit.utils.xpath_first_check(errorbox, './p')
                msg = 'Error message found in document: %s' % message_element.text
                self.fail(msg)
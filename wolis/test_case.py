import owebunit
import owebunit.utils
import utu
import lxml.etree
import os
import os.path
import random
import re
import urlparse
import xml.sax.saxutils
from . import config
from . import utils

xpath_first = owebunit.utils.xpath_first
xpath_first_check = owebunit.utils.xpath_first_check

class WolisTestCase(utu.adjust_test_base(owebunit.WebTestCase)):
    def __init__(self, *args, **kwargs):
        super(WolisTestCase, self).__init__(*args, **kwargs)
        
        self.conf = config.Config()
        
        self.config.host = self.conf.test_url
        self.config.save_responses = True
        self.config.save_dir = self.conf.responses_dir
        self._sid = None
    
    @property
    def phpbb_version(self):
        return utils.current.phpbb_version or utils.PhpbbVersion(self.conf)
    
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
        password_name = xpath_first_check(doc, '//input[@type="password"]').attrib['name']
        
        params = {
            'username': username,
            password_name: password,
        }
        
        params = owebunit.extend_params(form.params.list, params)
        self.post(form.computed_action, body=params)
        self.assert_successish()
        
        assert 'You have successfully authenticated' in self.response.body
        
        self.find_sid()
    
    def change_acp_knob(self, link_text, check_page_text, name, value):
        '''Note: requires an estableshed acp session.
        '''
        
        start_url = '/adm/index.php'
        self.get_with_sid(start_url)
        self.assert_successish()
        
        assert 'Board statistics' in self.response.body
        
        url = self.link_href_by_text(link_text)
        
        # already has sid
        self.get(urlparse.urljoin(start_url, url))
        self.assert_successish()
        
        assert check_page_text in self.response.body
        
        assert len(self.response.forms) == 1
        form = self.response.forms[0]
        
        self.check_form_key_delay()
        
        params = {
            name: value,
        }
        params = owebunit.extend_params(form.params.list, params)
        self.post(form.computed_action, body=params)
        self.assert_successish()
        
        assert 'Configuration updated successfully' in self.response.body
    
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
        link = xpath_first_check(doc, xpath)
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
        
        cache_path = os.path.join(self.conf.test_root_phpbb, 'cache')
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
        
        if session.response.code == 503:
            msg = 'Expected response to be successful, but was 503'
            if session.response.header_dict['content-type'].lower().startswith('text/html'):
                doc = session.response.lxml_etree
                if xpath_first(doc, '//title[text()="General Error"]') is not None:
                    message = xpath_first_check(doc, '//h1[text()="General Error"]/..')
                    xml = lxml.etree.tostring(message)
                    from . import html2text
                    text = html2text.html2text(xml)
                    msg += "\n" + text
            self.fail(msg)
        session.assert_status(200)
        self.assert_no_php_spam(session)
        self.assert_no_phpbb_error(session)
    
    def assert_no_php_spam(self, session=None):
        if session is None:
            session = self
        
        spams = [
            'Fatal error:',
            'phpBB Debug',
            'PHP Warning',
            'PHP Notice',
        ]
        for spam in spams:
            if spam in session.response.body:
                lines = session.response.body.split("\n")
                spam_lines = []
                for line in lines:
                    if spam in line:
                        if len(spam_lines) >= 5:
                            # more than 5 lines were found
                            spam_lines.append('(and more)')
                            break
                        # account for possible carriage returns
                        spam_lines.append(utils.naive_strip_html(line.strip()))
                msg = "PHP spam found in response body:\n%s" % "\n".join(spam_lines)
                self.fail(msg)
        
        # xdebug php warning
        assert not re.search(r'Warning: .* in .* on line ', session.response.body)
    
    def assert_no_phpbb_error(self, session=None):
        '''Checks if the document appears to have a phpBB error in it.
        
        The check is somewhat fuzzy.
        '''
        
        if session is None:
            session = self
        
        if not session.response.header_dict['content-type'].lower().startswith('text/html'):
            return
        
        doc = self.response.lxml_etree
        errorbox = owebunit.utils.xpath_first(doc, '//div[@class="errorbox"]')
        if errorbox is not None:
            severity = xpath_first_check(errorbox, './h3').text.strip()
            if severity != 'Warning':
                message_element = xpath_first_check(errorbox, './p')
                msg = 'Error message found in document: %s' % message_element.text
                self.fail(msg)

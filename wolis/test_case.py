import webracer
import webracer.utils
import utu
import lxml.etree
import os
import os.path
import random
import re
import xml.sax.saxutils
from . import config
from . import utils
from . import helpers

xpath_first = webracer.utils.xpath_first
xpath_first_check = webracer.utils.xpath_first_check

class ValidationError(StandardError):
    pass

class WolisTestCase(utu.adjust_test_base(webracer.WebTestCase), helpers.Helpers):
    def __init__(self, *args, **kwargs):
        super(WolisTestCase, self).__init__(*args, **kwargs)
        
        self.conf = utils.current.config or config.Config()
        
        self.config.host = self.conf.test_url
        self.config.save_responses = True
        self.config.save_dir = self.conf.responses_dir
        self._sid = None
    
    @property
    def phpbb_version(self):
        return utils.current.phpbb_version or utils.PhpbbVersion(self.conf)
    
    def find_sid(self):
        cookie_names = self._agent._cookie_jar.keys()
        sid_name = None
        for name in cookie_names:
            if name.endswith('_sid'):
                if sid_name is None:
                    sid_name = name
                else:
                    raise ValueError, 'Duplicate sid cookies detected: %s and %s' % (sid_name, name)
        self._sid = self._agent._cookie_jar[sid_name].value
    
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
    
    # contrary to the name this uses re.search, not re.match
    def link_href_by_href_match(self, regexp_str):
        for link in self.response.lxml_etree.iter('a'):
            if 'href' not in link.attrib:
                continue
            if re.search(regexp_str, link.attrib['href']):
                return link.attrib['href']
        self.fail('No link found matching %s' % regexp_str)
    
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
    
    def assert_successish(self, session=None, check_errorbox=True):
        if session is None:
            session = self
        
        if session.response.code == 503:
            msg = 'Expected response to be successful, but was 503'
            if session.response.headers['content-type'].lower().startswith('text/html'):
                doc = session.response.lxml_etree
                if xpath_first(doc, '//title[text()="General Error"]') is not None:
                    message = xpath_first_check(doc, '//h1[text()="General Error"]/..')
                    text = utils.text_content(message)
                    msg += "\n" + text
            self.fail(msg)
        
        session.assert_status(200)
        self.assert_no_php_spam(session)
        self.validate_markup(session)
        
        if check_errorbox:
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
        
        if not session.response.headers['content-type'].lower().startswith('text/html'):
            return
        
        doc = self.response.lxml_etree
        errorbox = webracer.utils.xpath_first(doc, '//div[@class="errorbox"]')
        if errorbox is not None:
            severity = xpath_first_check(errorbox, './h3').text.strip()
            if severity != 'Warning':
                message_element = xpath_first_check(errorbox, './p')
                msg = 'Error message found in document: %s' % message_element.text
                self.fail(msg)
    
    def validate_markup(self, session=None):
        '''Validates response body, if response is XML or HTML content.
        '''
        
        if session is None:
            session = self
        
        if len(session.response.raw_body) == 0:
            return
        
        content_type = session.response.header_dict['content-type'].lower()
        # drop charset
        content_type = re.sub(r';.*', '', content_type)
        if re.search(r'\bxml\b', content_type):
            self.validate_xml(session.response, session.response.body)
        elif re.search(r'\bhtml\b', content_type):
            self.validate_html(session.response, session.response.body)
    
    def validate_xml(self, response, text):
        import lxml.etree
        doc = lxml.etree.XML(text)
    
    def validate_html_lxml(self, response, text):
        import lxml.etree
        parser = lxml.etree.HTMLParser(recover=False)
        try:
            doc = lxml.etree.HTML(text, parser)
        except lxml.etree.XMLSyntaxError as e:
            print e
            utils.current.validation_errors.append((response.request_url, text, str(e)))
    
    def validate_html_html5lib(self, response, text):
        # http://12-oz-programmer.blogspot.com/2012/09/django-html5lib-validating-middleware.html
        
        import html5lib.html5parser
        import html5lib.treebuilders
        
        treebuilder = html5lib.treebuilders.getTreeBuilder('simpleTree')
        parser = html5lib.html5parser.HTMLParser(tree=treebuilder, strict=True)
        # this should be fine for validation
        text = text.replace("\t", '        ')
        try:
            doc = parser.parse(text)
        except:
            pass
        if parser.errors:
            # format output
            out = []
            lines = text.splitlines()
            for (row, col), e, d in parser.errors:
                out.append('%s, %s' % (e, d))
                for x in range(max(0, row - 3), min(len(lines), row + 1)):
                    out.append(lines[x])
                #offender = lines[row]
                #before = offender[:col]
                #tabs = before.count("\t")
                # html5lib seems to count each tab as two spaces
                out.append(' ' * col + '^')
            out = '\n'.join(out)        #print text
            #raise ValidationError(out)
            utils.current.validation_errors.append(self.response.request_uri, text, out)
    
    def validate_html(self, response, text):
        self.validate_html_lxml(response, text)
        self.validate_html_html5lib(response, text)
    
    #validate_html = validate_html_lxml
    
    def find_current_page(self):
        if self.phpbb_version < (3, 1, 0):
            # the first strong is the active page
            # http://stackoverflow.com/questions/1390568/xpath-how-to-match-attributes-that-contain-a-certain-string
            active = xpath_first_check(self.response.lxml_etree, '//li[contains(@class, "pagination")]//strong')
            page = int(active.text)
        else:
            active = xpath_first_check(self.response.lxml_etree, '//li[@class="active"]')
            text = lxml.etree.tostring(active, method='text').strip()
            page = int(text)
        return page

# -*- coding: utf-8 -*-

import re, os
import webracer.utils
from wolis import utils
from wolis.test_case import WolisTestCase

class SphinxConfigTest(WolisTestCase):
    def test_obtain_config(self):
        self.login('morpheus', 'morpheus')
        self.acp_login('morpheus', 'morpheus')
        
        start_url = '/adm/index.php'
        self.get_with_sid(start_url)
        self.assert_successish()
        
        assert 'Board statistics' in self.response.body
        
        url = self.response.urljoin(self.link_href_by_text('Search settings'))
        assert 'i=acp_search' in url
        assert 'mode=settings' in url
        self.get(url)
        self.assert_successish()
        
        assert 'Here you can define what search backend will be used' in self.response.body
        assert 'Sphinx config file' in self.response.body
        
        form = self.response.form()
        elements = form.elements.mutable
        elements.set_value('config[fulltext_sphinx_data_path]', self.conf.sphinx_data_path + '/')
        # change port to something non-default
        elements.set_value('config[fulltext_sphinx_port]', str(self.conf.sphinx_searchd_port))
        self.post(form.computed_action, elements.params.list)
        self.assert_successish()
        
        assert 'Configuration updated successfully.' in self.response.body
        
        self.get(url)
        self.assert_successish()
        
        doc = self.response.lxml_etree
        # wtfs:
        # 1. unclosed span in sphinx config file line
        # 2. textarea has no name, no id, no class
        # 3. textarea contents is not html-escaped, but contains angle brackets
        element = webracer.utils.xpath_first_check(doc,
            '//label[@for="fulltext_sphinx_config_file"]/ancestor::dl//textarea')
        config_text = element.text
        #form = self.response.form()
        #config_text = form.params.dict['config[fulltext_sphinx_config_file]']
        
        original_pid = r'pid_file = %s' % os.path.join(self.conf.sphinx_data_path, 'searchd.pid')
        assert original_pid in config_text
        replaced_pid = r'pid_file = %s' % self.conf.sphinx_pidfile_path
        config_text = config_text.replace(original_pid, replaced_pid)
        
        original_log = os.path.join(self.conf.sphinx_data_path, 'log')
        assert original_log in config_text
        config_text = config_text.replace(original_log, self.conf.sphinx_log_path)
        
        utils.mkdir_p(self.conf.sphinx_root)
        with open(self.conf.sphinx_config_path, 'w') as f:
            f.write(config_text)
        
        match = re.search(r'source source_phpbb_(\w+)_main', config_text)
        assert match
        sphinx_id = match.group(1)
        with open(self.conf.sphinx_id_path, 'w') as f:
            f.write(sphinx_id)
        
        if self.conf.sphinx_cmd_prefix:
            cmd = self.conf.sphinx_cmd_prefix
            utils.run(cmd + ['rm', '-rf', self.conf.sphinx_data_path, self.conf.sphinx_log_path], no_check=True)
        else:
            import shutil
            shutil.rmtree(self.conf.sphinx_data_path)
            shutil.rmtree(self.conf.sphinx_log_path)
        
        utils.mkdir_p(self.conf.sphinx_data_path)
        utils.mkdir_p(self.conf.sphinx_log_path)
        
        if self.conf.sphinx_cmd_prefix:
            os.chmod(self.conf.sphinx_data_path, 0o777)
            os.chmod(self.conf.sphinx_log_path, 0o777)
            # for pid file
            os.chmod(self.conf.sphinx_root, 0o777)

if __name__ == '__main__':
    import unittest
    unittest.main()

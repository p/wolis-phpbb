# depends:
# python.install
#
# after:
# casper.login
#
# phpbb_version:
# >=3.1.0
#
# db:
# postgres

utils = require './utils'
search_index = require './search_index'

d = ->
  console.log arguments...

base = global.wolis.config.test_url

casper.start()

casper.then ->
  utils.acp_login 'morpheus', 'morpheus',

casper.then ->
  @click utils.xpath('//input[@id="action_purge_sessions"]')
  @waitForResource /i=acp_main.*mode=main/

utils.thensaveresponse ->
  @test.assertTextExists 'Are you sure you wish to purge all sessions?'
  @click utils.xpath('//input[@value="Yes"]')
  # test http://tracker.phpbb.com/browse/PHPBB3-11442
  @waitForText 'Sessions successfully purged.'

utils.thensaveresponse ->
  true

casper.run ->
  @test.done()

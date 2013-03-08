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
# mysql*

utils = require './wolisutils'
search_index = require './search_index'

d = ->
  console.log arguments...

base = global.wolis.config.test_url

casper.start()

casper.then ->
  utils.acp_login 'morpheus', 'morpheus',

casper.then ->
  search_index.create_search_index 'Sphinx Fulltext'

casper.run ->
  @test.done()

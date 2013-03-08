# depends:
# python.install
#
# after:
# casper.login

utils = require './wolisutils'
search_index = require './search_index'

d = ->
  console.log arguments...

base = global.wolis.config.test_url

casper.start()

casper.then ->
  utils.acp_login 'morpheus', 'morpheus',

casper.then ->
  if utils.phpbb_version_check('<3.1.0')
    label = 'Fulltext native'
  else
    label = 'phpBB Native Fulltext'
  search_index.delete_search_index label

casper.run ->
  @test.done()

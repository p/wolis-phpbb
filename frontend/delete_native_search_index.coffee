# depends:
# python.install
#
# after:
# casper.login

utils = require './utils'
search_index = require './search_index'

d = ->
  console.log arguments...

base = global.wolis.config.test_url

casper.start()

casper.then ->
  utils.acp_login 'morpheus', 'morpheus',

casper.then ->
  search_index.delete_search_index 'phpBB Native Fulltext'

casper.run ->
  @test.done()

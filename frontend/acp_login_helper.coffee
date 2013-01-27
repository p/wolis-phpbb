# depends:
# python.install
#
# after:
# casper.login

utils = require './utils'

d = ->
  console.log arguments...

base = global.wolis.config.test_url

casper.start()

casper.then ->
  utils.acp_login 'morpheus', 'morpheus',

casper.run ->
  @test.done()

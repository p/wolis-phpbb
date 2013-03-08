# depends:
# python.install
#
# after:
# python.login

utils = require './wolisutils'

d = ->
  console.log arguments...

base = global.wolis.config.test_url

casper.start()

casper.then ->
  utils.login 'morpheus', 'morpheus',

casper.then ->
  @open base

utils.thensaveresponse ->
  @test.assertHttpStatus 200
  
  @test.assertTextExists 'Administration Control Panel'
  @click utils.xpath(utils.a_text_xpath('Administration Control Panel'))

utils.thensaveresponse ->
  @test.assertHttpStatus 200
  
  @test.assertTextExists 'To administer the board you must re-authenticate yourself.'
  password_name = @evaluate ->
    document.querySelector('input[type=password]').getAttribute('name')
  
  @evaluate utils.fixsubmit, 'form#login'
  fields = {username: 'morpheus'}
  fields[password_name] = 'morpheus'
  @fill 'form#login', fields, true

utils.thensaveresponse ->
  @test.assertHttpStatus 200
  
  @test.assertTextExists 'Proceed to the ACP'
  @click utils.xpath(utils.a_text_xpath('Proceed to the ACP'))

utils.thensaveresponse ->
  @test.assertHttpStatus 200
  
  @test.assertTextExists 'Thank you for choosing phpBB as your board solution.'

casper.run ->
  @test.done()

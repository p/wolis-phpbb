# depends:
# python.install
#
# after:
# python.login

utils = require './wolisutils'

d = ->
  console.log arguments...

base = global.wolis.config.test_url

casper.start base, ->
  @test.assertHttpStatus 200
  
  @test.assertTextExists 'Your first forum'
  @test.assertTextNotExists 'User Control Panel'
  
  # yuck at the selector
  @evaluate utils.fixsubmit, 'form.headerspace'
  #d @evaluate ->
    #$('form.headerspace')[0].parentNode.innerHTML
  @fill 'form.headerspace', {
    username: 'morpheus'
    password: 'morpheus'
  }, true
  #@click utils.xpath('//input[@value="Login"]')

utils.thensaveresponse ->
  #d @getCurrentUrl()
  #utils.savehtml @getHTML()
  
  @test.assertUrlMatch /ucp\.php.*mode=login/
  @test.assertHttpStatus 200
  
  errors = @evaluate ->
    errors = document.querySelector 'div[class=error]'
    if errors
      errors.innerHTML
    else
      ''
  if errors
    d "Possible errors: #{errors}"
  
  #d @getHTML()
  
  @test.assertTextExists 'You have been successfully logged in.'
  @test.assertTextExists 'User Control Panel'

casper.run ->
  @test.done()

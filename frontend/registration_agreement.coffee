# depends:
# python.install
# prosilver?

utils = require './wolisutils'

d = ->
  console.log arguments...

base = global.wolis.config.test_url

casper.start base + '/ucp.php?mode=register', ->
  @test.assertHttpStatus 200
  @test.assertExists 'input[value="I agree to these terms"]'
  
  @click 'input[value="I agree to these terms"]'

utils.thensaveresponse ->
  @test.assertHttpStatus 200
  @test.assertDoesntExist 'input[value="I agree to these terms"]'
  @test.assertTextExists 'Confirm password:'

casper.run ->
  @test.done()

d = ->
  console.log arguments...

casper.start 'http://func/ucp.php?mode=register', ->
  @test.assertHttpStatus 200
  @test.assertExists 'input[value="I agree to these terms"]'
  
  @click 'input[value="I agree to these terms"]'

casper.then ->
  @test.assertHttpStatus 200
  @test.assertDoesntExist 'input[value="I agree to these terms"]'
  @test.assertTextExists 'Confirm password:'

casper.run ->
  @test.done()
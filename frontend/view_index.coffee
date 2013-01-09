d = ->
  console.log arguments...

base = global.wolis.config.test_url

casper.start base, ->
  @test.assertHttpStatus 200
  
  # check that the index page has expected text
  @test.assertTextExists 'Your first forum'

casper.run ->
  @test.done()

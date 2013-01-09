d = ->
  console.log arguments...

base = global.wolisconfig.test_url

casper.start base, ->
  this.test.assertHttpStatus 200

casper.run ->
  @test.done()

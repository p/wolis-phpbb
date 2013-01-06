casper = require('casper').create()

d = ->
  console.log arguments...

casper.start 'http://func', ->
  this.test.assertHttpStatus 200

casper.run ->
  @test.done()
  ok = @test.getFailures().length == 0
  @test.renderResults(true, if ok then 0 else 5)

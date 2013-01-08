casper = require('casper').create()

d = ->
  console.log arguments...

casper.start 'http://func/ucp.php?mode=register&agreed=1', ->
  @test.assertExists '#tz_date'
  tz_value = @evaluate ->
    document.querySelector('#tz_date').value
  # Should match system time zone
  @test.assertMatch tz_value, /^GMT-05:00/

casper.run ->
  @test.done()
  ok = @test.getFailures().length == 0
  @test.renderResults(true, if ok then 0 else 5)

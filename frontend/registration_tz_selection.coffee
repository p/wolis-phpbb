# dependencies:
# python.install
# prosilver?
#
# after:
# casper.registration_agreement

d = ->
  console.log arguments...

base = global.wolis.config.test_url

casper.start base + '/ucp.php?mode=register&agreed=1', ->
  @test.assertExists '#tz_date'
  tz_value = @evaluate ->
    document.querySelector('#tz_date').value
  # Should match system time zone
  @test.assertMatch tz_value, /^GMT-05:00/

casper.run ->
  @test.done()

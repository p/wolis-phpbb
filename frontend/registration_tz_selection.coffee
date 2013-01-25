# depends:
# python.install
# prosilver?
#
# after:
# casper.registration_agreement
#
# phpbb_version:
# >=3.1.0

d = ->
  console.log arguments...

base = global.wolis.config.test_url

casper.start base + '/ucp.php?mode=register&agreed=1', ->
  @test.assertExists '#tz_date'
  tz_value = @evaluate ->
    document.querySelector('#tz_date').value
  # Should match system time zone
  # System time zone is our time zone
  offset_hours = (new Date()).getTimezoneOffset() / -60
  sign = if offset_hours < 0 then '-' else '+'
  offset = Math.abs(offset_hours)
  if offset < 10
    offset = '0' + offset
  # XXX does not handle fractional hour offsets
  @test.assertMatch tz_value, new RegExp("^GMT#{sign}#{offset}:00")

casper.run ->
  @test.done()

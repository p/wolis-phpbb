# depends:
# python.install
# prosilver?
#
# after:
# casper.login_helper
#
# phpbb_version:
# >=3.1.0

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
  
  @test.assertTextExists 'Your first forum'
  @click utils.xpath(utils.a_text_xpath('Your first forum'))

utils.thensaveresponse ->
  # on viewforum
  @test.assert(/viewforum/.test(@getCurrentUrl()))
  
  @test.assertHttpStatus 200
  @test.assertTextExists 'Welcome to phpBB3'
  
  @click utils.xpath(utils.a_text_xpath('Welcome to phpBB3'))

utils.thensaveresponse ->
  # on viewtopic
  @test.assert(/viewtopic/.test(@getCurrentUrl()))
  
  @test.assertHttpStatus 200
  @test.assertNotExists utils.a_text_xs('Remove from bookmarks')
  @test.assertExists utils.a_text_xs('Bookmark topic')
  
  @click utils.xpath(utils.a_text_xpath('Bookmark topic'))
  
  @waitForResource /viewtopic\.php.*bookmark=1/

casper.then ->
  @test.assertExists utils.a_text_xs('Remove from bookmarks')
  @test.assertNotExists utils.a_text_xs('Bookmark topic')

# unbookmark
casper.then ->
  @click utils.xpath(utils.a_text_xpath('Remove from bookmarks'))
  
  # This is iffy because the same url was loaded previously.
  # On freebsd this works, on linux it does not.
  # Wait for the selector instead
  #@waitForResource /viewtopic\.php.*bookmark=1/
  
  @waitForSelector utils.a_text_xs('Bookmark topic')

casper.then ->
  @test.assertNotExists utils.a_text_xs('Remove from bookmarks')
  # We now wait for this, therefore no point in checking it
  #@test.assertExists utils.a_text_xs('Bookmark topic')

casper.run ->
  @test.done()

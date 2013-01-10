# dependencies:
# python.install
# prosilver?
#
# after:
# casper.login_helper

utils = require './utils'

d = ->
  console.log arguments...

base = global.wolis.config.test_url

casper.start()

casper.then ->
  utils.login 'morpheus', 'morpheus',

casper.then ->
  @open base

casper.then ->
  @test.assertHttpStatus 200
  
  @test.assertTextExists 'Your first forum'
  @click utils.xpath('//a[text()="Your first forum"]')

casper.then ->
  # on viewforum
  @test.assert(/viewforum/.test(@getCurrentUrl()))
  
  @test.assertHttpStatus 200
  @test.assertTextExists 'Welcome to phpBB3'
  
  @click utils.xpath('//a[text()="Welcome to phpBB3"]')

casper.then ->
  # on viewtopic
  @test.assert(/viewtopic/.test(@getCurrentUrl()))
  
  @test.assertHttpStatus 200
  @test.assertTextNotExists 'Remove from bookmarks'
  @test.assertTextExists 'Bookmark topic'
  
  @click utils.xpath('//a[text()="Bookmark topic"]')
  
  @waitForResource /viewtopic\.php.*bookmark=1/

casper.then ->
  @test.assertTextExists 'Remove from bookmarks'
  @test.assertTextDoesntExist 'Bookmark topic'

casper.run ->
  @test.done()

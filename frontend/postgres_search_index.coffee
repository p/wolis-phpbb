# depends:
# python.install
#
# after:
# casper.login
#
# db:
# postgres

utils = require './utils'

d = ->
  console.log arguments...

base = global.wolis.config.test_url

casper.start()

casper.then ->
  utils.acp_login 'morpheus', 'morpheus',

casper.then ->
  @open base

utils.thensaveresponse ->
  @test.assertHttpStatus 200
  
  @test.assertTextExists 'Administration Control Panel'
  @click utils.xpath(utils.a_text_xpath('Administration Control Panel'))

utils.thensaveresponse ->
  @test.assertHttpStatus 200
  
  @test.assertTextExists 'Thank you for choosing phpBB as your board solution.'
  @click utils.xpath(utils.acp_tab_xpath('Maintenance'))

utils.thensaveresponse ->
  @test.assertHttpStatus 200
  
  @click utils.xpath(utils.acp_sidebar_xpath('Search index'))

utils.thensaveresponse ->
  @test.assertHttpStatus 200

  @test.assertTextExists 'Here you can manage the search backend’s indexes.'
  
  found = @evaluate ->
    coll = document.getElementsByTagName('caption')
    found = false
    Array.prototype.forEach.call coll, (elt)->
      return if found
      if elt.textContent.indexOf('PostgreSQL Fulltext') >= 0
        # found
        while elt.tagName.toLowerCase() != 'form'
          elt = elt.parentNode
        elt = elt.querySelector 'input[type=submit]'
        if elt.getAttribute('value') == 'Create index'
          elt.click()
          found = true
        else
          # will break but fail assertion below
          found = 2
    found
  
  @test.assert found
  
  @waitForText 'Successfully indexed all posts in the board database.'

casper.run ->
  @test.done()

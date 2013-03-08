utils = require './wolisutils'

d = ->
  console.log arguments...

exports.create_search_index = (name)->
  create_or_delete name, 'Create index', 'Successfully indexed all posts in the board database.'

exports.delete_search_index = (name)->
  create_or_delete name, 'Delete index', 'Successfully deleted the search index for this backend.'

create_or_delete = (name, buttontext, success_msg)->
  base = global.wolis.config.test_url

  casper.open base

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
    
    expr = '//caption[contains(text(),"' + name + '")]'
    @test.assertExists utils.xpath(expr)
    submit_expr = expr + '/ancestor::form//input[@type="submit"]'
    @test.assertExists utils.xpath(submit_expr)
    submit_text_expr = expr + '/ancestor::form//input[@type="submit"][@value="' + buttontext + '"]'
    @test.assertExists utils.xpath(submit_text_expr)
    @click utils.xpath(submit_expr)
    
    utils.assertWaitForText success_msg

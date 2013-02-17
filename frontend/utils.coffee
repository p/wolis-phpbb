fs = require 'fs'
version = require './version'

d = ->
  console.log arguments...

# Some easier to type aliases
casper.test.assertTextNotExists = casper.test.assertTextDoesntExist
tojson = JSON.stringify

exports.xpath = (expr)->
  {type: 'xpath', path: expr}

exports.a_text_xpath = (text)->
  if text.indexOf('"') >= 0
    throw 'Double quotes in argument are not allowed: ' + text
  '//a[text()="' + text + '"]'

exports.acp_tab_xpath = (text)->
  # XXX does not quote text
  #'//div[@id="tabs"]//a[descendant-or-self::*/text()="' + text + '"]'
  '//div[@id="tabs"]//span[text()="' + text + '"]/..'

exports.acp_sidebar_xpath = (text)->
  # XXX does not quote text
  #'//div[@id="tabs"]//a[descendant-or-self::*/text()="' + text + '"]'
  '//div[@id="menu"]//span[text()="' + text + '"]/..'

exports.a_text_xs = ->
  exports.xpath(exports.a_text_xpath(arguments...))

exports.savehtml = savehtml = (html)->
  now = new Date
  timestamp = (now.getTime() / 1000).toString()
  filename = 'response_' + timestamp
  path = wolis.config.responses_dir + '/' + filename
  f = fs.open path, 'w'
  f.write html
  f.close()

exports.login = (username, password)->
  base = global.wolis.config.test_url
  
  casper.open base
  
  casper.then ->
    @test.assertHttpStatus 200
    
    @test.assertTextExists 'Your first forum'
    @test.assertTextNotExists 'User Control Panel'
    
    # yuck at the selector
    @evaluate fixsubmit, 'form.headerspace'
    @fill 'form.headerspace', {
      username: username
      password: password
    }, true
  
  exports.thensaveresponse ->
    @test.assertUrlMatch /ucp\.php.*mode=login/
    @test.assertHttpStatus 200
    
    errors = @evaluate ->
      errors = document.querySelector 'div[class=error]'
      if errors
        errors.innerHTML
      else
        ''
    if errors
      d "Possible errors: #{errors}"
    
    @test.assertTextExists 'You have been successfully logged in.'
    @test.assertTextExists 'User Control Panel'

exports.acp_login_only = (username, password)->
  base = global.wolis.config.test_url
  
  casper.open base
  
  exports.thensaveresponse ->
    @test.assertHttpStatus 200
    
    @test.assertTextExists 'Your first forum'
    @test.assertTextExists 'User Control Panel'
    @test.assertTextExists 'Administration Control Panel'
    
    @click exports.xpath(exports.a_text_xpath('Administration Control Panel'))

  exports.thensaveresponse ->
    @test.assertHttpStatus 200
    
    @test.assertTextExists 'To administer the board you must re-authenticate yourself.'
    password_name = @evaluate ->
      document.querySelector('input[type=password]').getAttribute('name')
    
    @evaluate exports.fixsubmit, 'form#login'
    fields = {username: username}
    fields[password_name] = password
    @fill 'form#login', fields, true

  exports.thensaveresponse ->
    @test.assertHttpStatus 200
    
    @test.assertTextExists 'Proceed to the ACP'
    @click exports.xpath(exports.a_text_xpath('Proceed to the ACP'))

exports.acp_login = (username, password)->
  exports.login username, password
  
  casper.then ->
    exports.acp_login_only username, password

exports.fixsubmit = fixsubmit = (selector)->
  form = document.querySelector selector
  for element in form.elements
    if ((element.tagName.toLowerCase() == 'input' ||
        element.tagName.toLowerCase() == 'button') &&
        element.type.toLowerCase() == 'submit')
      
      if element.name != undefined && element.value != undefined
        hidden = document.createElement('input')
        hidden.type = 'hidden'
        hidden.name = element.name
        hidden.value = element.value
        hidden.className = 'phantomjs-form-submit-workaround'
        form.appendChild hidden
        break

exports.thensaveresponse = (done)->
  casper.then ->
    savehtml @getHTML()
    done.call(this, arguments)

exports.evaluate = (fn, args...)->
  rv = casper.evaluate (fn, args)->
    try
      rv = fn(args...)
      [true, rv]
    catch e
      [false, e]
  , fn, args
  casper.test.assert rv != null, 'evaluate return value is not null'
  [ok, rv] = rv
  unless ok
    # This does not seem to work
    #throw rv
    
    d 'Exception evaluating javascript in phantomjs:'
    d rv.message
    d rv.stack
    throw "Failed evaluating javascript in phantomjs: #{rv.message}"
  rv

exports.assertwaitfortext = exports.assertWaitForText = (text)->
  casper.waitForText text, ->
    true
  , ->
    #@test.fail 'Text not found: ' + text
    # https://github.com/n1k0/casperjs/issues/369
    d 'Text not found: ' + text
    d 'Exiting due to casper bug'
    @exit -24

exports.phpbb_version_check = (spec)->
  version.version_check(spec, global.wolis.phpbb_version)

fs = require 'fs'

d = ->
  console.log arguments...

# Some easier to type aliases
casper.test.assertTextNotExists = casper.test.assertTextDoesntExist

exports.xpath = xpath = (expr)->
  {type: 'xpath', path: expr}

exports.savehtml = savehtml = (html)->
  now = new Date
  timestamp = (now.getTime() / 1000).toString()
  filename = 'response_' + timestamp
  path = wolis.config.responses_dir + '/' + filename
  f = fs.open path, 'w'
  d path, f
  f.write html
  f.close()

#exports.login = login = (username, password, done)->

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

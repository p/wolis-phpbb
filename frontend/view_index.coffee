casper = require('casper').create()

d = ->
  console.log arguments...

casper.start 'http://func', ->
  this.test.assertHttpStatus 200

casper.run()

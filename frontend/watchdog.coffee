watchdog = ()->
  console.log 'Aborting test run due to timeout (2 minutes)'
  phantom.exit(20)

setTimeout watchdog, 120000

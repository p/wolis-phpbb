watchdog = ()->
  console.log 'Aborting test run due to timeout (1 minute)'
  phantom.exit(20)

setTimeout watchdog, 60000

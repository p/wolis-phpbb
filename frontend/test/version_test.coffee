assert = require 'assert'
version = require '../lib/version'

d = console.log

describe 'version', ->
  it 'should work', ->
    check = (args)->
      [spec, check, expected] = args
      actual = version.version_check(spec, check)
      assert.equal(expected, actual, "failed for [#{args.join(', ')}]")

    [
      ['>=3.0.0', [3,0,0], true]
      ['>=3.0.0', [3,1,0], true]
      ['<3.0.0', [3,0,0], false]
      ['<3.0.0', [3,1,0], false]
    ].map check

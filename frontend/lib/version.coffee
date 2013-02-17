d = ->
  console.log arguments...

cmpfuncs = {
  '>=': (a, b)->
    a >= b
  '<': (a, b)->
    a < b
}

docheck = (cmpfn, against, value)->
  for i in [0...against.length]
    v = parseInt(value[i])
    a = parseInt(against[i])
    if v != a
      return cmpfn(v, a)
  cmpfn(v, a)

exports.version_check = (spec, check)->
  for op of cmpfuncs
    if spec.slice(0, op.length) == op
      value = spec.slice(op.length).split('.')
      return docheck(cmpfuncs[op], value, check)
  throw "Unrecognized specification: #{spec}"

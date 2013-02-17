d = console.log

cmpfuncs = {
  '>=': (a, b)->
    a >= b
  '<': (a, b)->
    a < b
}

docheck = (cmpfn, value, against)->
  for i in [0...against.length]
    v = parseInt(value[i])
    a = parseInt(against[i])
    if v != a
      return cmpfn(v, a)
  cmpfn(v, a)

exports.version_check = (spec, against)->
  for op of cmpfuncs
    if spec.slice(0, op.length) == op
      value = spec.slice(op.length).split('.')
      return docheck(cmpfuncs[op], value, against)
  throw "Unrecognized specification: #{spec}"

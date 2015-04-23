var semi = require('semi')
var cmd = process.argv[2]

semi.on('error', function (e) {
  process.stderr.write(
    '[semi error] ' +
    e.message + ' at ' + e.line + ':' + e.column
  )
})

process.stdin.on('data', function (buffer) {
  process.stdout.write(semi[cmd](buffer.toString()))
})
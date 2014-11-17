var semi = require('semi')
var cmd = process.argv[2]
process.stdin.on('data', function (buffer) {
  process.stdout.write(semi[cmd](buffer.toString()))
})
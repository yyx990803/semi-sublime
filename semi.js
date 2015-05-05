var semi = require('semi')
var leading = checkLeadingOption()
var cmd = process.argv[2]
var file = ''

semi.on('error', function (e) {
  process.stderr.write(
    '[semi error] ' +
    e.message + ' at ' + e.line + ':' + e.column + '\n'
  )
})

process.stdin.on('data', function (buffer) {
  file += buffer.toString()
})

process.stdin.on('end', function () {
  process.stdout.write(semi[cmd](file))
})

function checkLeadingOption () {
  var settings = require('fs').readFileSync(__dirname + '/semi.sublime-settings')
  settings = JSON.parse(settings)
  return settings.leading
}
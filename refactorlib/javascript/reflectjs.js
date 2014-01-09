/******************************************************************************
 * This script was developed using the nodejs, version 0.10.24
 *
 * References:
 *      https://developer.mozilla.org/en/SpiderMonkey/Shell_global_objects
 *      https://npmjs.org/package/reflect
 *****************************************************************************/
var Reflect = require('reflect');
var doc = '';

process.stdin.resume();
process.stdin.on('data', function(chunk) {
    doc += chunk;
});

process.stdin.on('end', function() {
    process.stdout.write(JSON.stringify(Reflect.parse(doc)));
    process.stdin.pause()
});

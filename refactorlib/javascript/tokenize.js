/******************************************************************************
 * This script was developed using the SpiderMonkey shell (smjs), version 185
 * 
 * Reference:
 *		https://developer.mozilla.org/en/SpiderMonkey/Shell_global_objects
 *****************************************************************************/
var doc = '';
while ( (line = readline()) !== null ) {
	doc += line + '\n';
}
putstr(JSON.stringify(Reflect.parse(doc)));

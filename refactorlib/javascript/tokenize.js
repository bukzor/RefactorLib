/******************************************************************************
 * This script was developed using the SpiderMonkey shell (smjs), version 185
 *
 * Input will always be interpreted as ending with newline. I don't see any way
 * to do it correctly...
 * 
 * Reference:
 *		https://developer.mozilla.org/en/SpiderMonkey/Shell_global_objects
 *****************************************************************************/
var doc = '';
while ( (line = readline()) !== null ) {
	doc += line + '\n';
}
putstr(JSON.stringify(Reflect.parse(doc)));

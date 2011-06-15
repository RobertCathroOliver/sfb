/* global module */
SFB = typeof SFB == 'undefined' ? {} : SFB;
SFB.version = 0.1;
SFB.make_option_parser = function(defaults) {
    return function(options) {
	if (!options) { return defaults;}
	for (var o in defaults) {
	    if (defaults.hasOwnProperty(o) && typeof options[o] == 'undefined') {
		 options[o] = defaults[o];
	    }
	}
	return options;
    };
};

if (typeof Object.create !== 'function') {
    Object.create = function(o) {
	function F() {}
	F.prototype = o;
	return new F();
    };
}



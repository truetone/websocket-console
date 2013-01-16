$(function ()
{
	/* Modernizr */
	Modernizr.load(
	{
		test: Modernizr.websockets,
		yep: 'section-sockets.js',
		nope: 'nosockets.js'
	});
});

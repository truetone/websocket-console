$(function ()
{
	var socket = new WebSocket("ws://localhost:9000");

	socket.onmessage = function (e)
	{
		rcvdData = JSON.pare(e.data);
		toConsole(rcvdData);
	};

	function toConsole(d)
	{
		$("#console").prepend(d);
	}
});

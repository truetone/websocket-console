$(function()
{
	var socket = new WebSocket("ws://localhost:9000" + window.location.pathname);

	console.log(window.location.pathname);

	socket.onmessage = function(e)
	{
        console.log(e.data);
	};

	$('button').click(function()
	{
		var msg = $('#test').data('section');
		var id = $(this).attr('id');
		var data = '{"' + id + '": "' + msg + '"}';

		socket.send(data);
		$('#console').append('<p>Sent: ' + data);
	});

	function echoRcvd(d)
	{
		$('#console').append('<p>Received: ' + d);
	}
});


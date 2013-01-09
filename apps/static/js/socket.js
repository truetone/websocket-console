$(function()
{
	var socket = new WebSocket("ws://localhost:9000");

	socket.onmessage = function(e)
	{
		returnedData = JSON.parse(e.data);

		echoRcvd(returnedData);
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


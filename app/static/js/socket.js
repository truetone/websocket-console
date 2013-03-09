$(function()
{
	var socket = new WebSocket("ws://localhost:9000" + window.location.pathname);

	socket.onopen = function(msg)
	{
		$('#console').append('<p>WebSocket connection established.');
	}

	socket.onclose = function(msg)
	{
		$('#console').append('<p>WebSocket connection closed.');
	}

	socket.onmessage = function(msg)
	{
		json = JSON.parse(msg.data);

		if (json.cmd !== undefined)
		{
			$('#console').append('<p>Hey! I received a command!');

			if (json.cmd.cmd !== undefined && json.cmd.cmd === 'chcolor')
			{
				$('#console').append('<p>I\'m supposed to change color.');

				if (json.cmd.val !== undefined)
				{
					$("#console").append('<p>The page should be ' + json.cmd.val + ' now.');
					$('body').css('background-color',  json.cmd.val);
				}
			}
			else
			{
				console.log('We couldn\'t determine the command');
			}
		}
		else
		{
			console.log(json)
		}
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


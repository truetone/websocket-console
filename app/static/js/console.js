$(function ()
{
	/* Handlebars templating stuff. */
	var clientsSource = $('#clients-template').html();
	var clientsTemplate = Handlebars.compile(clientsSource);

	/* socket connection */
	var socket = new WebSocket("ws://fullyarmedandoperational.com:9000" + window.location.pathname);

	socket.onopen = function(e)
	{
		console.log('Socket connection established!');
	}

	socket.onclose = function(e)
	{
		console.log('Socket connection closed. ');
	}

	socket.onerror = function(e)
	{
		console.log('Error: ' + e)
	}

	socket.onmessage = function(msg)
	{
		try
		{
			payload = JSON.parse(msg.data);
			switch(payload.cmd)
			{
				case "updateclients":
					$('section[role="main"]').text('')
						for(var section in payload.data)
						{
							$('section[role="main"]').append(clientsTemplate(
							{
								'section': section,
								'clients': payload.data[section]
							}));
						}
					console.log("Updated client listing.");
					break;
				default:
					console.log("Received invalid command!");
			}
		}
		catch (e)
		{
			console.log(msg);
		}
	};

	$('.color-changer').click(function ()
	{
		var btn = $(this);
		var cmd = btn.data('command');
		var stn = btn.data('section');
		var clr = btn.data('color');
		var msg = '{"cmd": {"cmd": "' + cmd + '", "val": "' + clr + '", "stn": "' + stn + '"}}';

		console.log(cmd)
		console.log(msg)

		// Set up cmd and section up as json and send them to the websocket server
		socket.send(msg);
	});

	function toConsole(d)
	{
		$("#console").prepend(d);
	}
});

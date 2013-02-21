$(function ()
{
	var clientsSource = $('#clients-template').html();
	var clientsTemplate = Handlebars.compile(clientsSource);

	var socket = new WebSocket("ws://localhost:9000" + window.location.pathname);

	socket.onmessage = function(e){
		payload = JSON.parse(e.data);
		switch(payload.cmd) {
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
	};

	$('.color-changer').click(function ()
	{
		var btn = $(this);
		var cmd = btn.data('cmd');
		var stn = btn.data('section');
		var clr = btn.data('color');
		var data = {"cmd" : {
						cmd : {
							"data" : clr,
							"stn" : stn
							}
						}
					};

		// Set up cmd and section up as json and send them to the websocket server
		socket.send(data);
	});

	function toConsole(d)
	{
		$("#console").prepend(d);
	}
});

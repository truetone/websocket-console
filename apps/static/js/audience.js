$(function ()
{
	var eventSource = new EventSource('/event-stream');

	eventSource.onmessage = function (message)
	{
		$('#console').append(message.data + '<br>');
	};
});

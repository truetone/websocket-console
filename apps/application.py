import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer

gevent.monkey.patch_all()

from flask import Flask, render_template, request, Response

app = Flask(__name__)

def event_stream():
	return 'data: hello world!\n\n'

@app.route('/event-stream')
def server_side_events():
	return Response(
		event_stream(),
		mimetype='text/event-stream')

@app.route('/')
@app.route('/section/<section>')
def index(section=None):
	return render_template('index.html', section=section)

if __name__ == '__main__':
	app.run(debug=True)

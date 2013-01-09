import flask, gevent, tweepy
import gevent.monkey
import config
from gevent.pywsgi import WSGIServer
from twisted.internet import reactor
from autobahn.websocket import WebSocketServerFactory, \
								WebSocketServerProtocol, \
								listenWS
from flask import Flask, render_template, request, Response

class EchoServerProtocol(WebSocketServerProtocol):
 
	def onMessage(self, msg, binary):
		self.sendMessage(msg, binary)
 
if __name__ == '__main__':
 
	factory = WebSocketServerFactory("ws://localhost:9000", debug = True)
	factory.protocol = EchoServerProtocol
	listenWS(factory)
	reactor.run()

gevent.monkey.patch_all()

session = dict()
db = dict()

app = Flask(__name__)

def event_stream():
	return 'data: hello world!\n\n'

def get_console_event():
	# Use a websocket connection to read events from a console page with states/events stored in javascript
	return True

def get_console_route():
	# Not sure if this is necessary. I might be able to handle routes w/ get_console_event
	return True

def event_router(event, route):
	event = get_console_event()
	route = get_console_route()

@app.route('/event-stream')
def server_side_events():
	return Response(
		event_stream(),
		mimetype='text/event-stream')

@app.route('/event-socket')
def socket_stream():
	return True #set this up to maintain a socket connection and relay data

@app.route('/')
@app.route('/section/<section>')
def index(section=None):
	return render_template('section.html', section=section)

@app.route('/authenticate')
def authenticate():

	auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback_url)

	try:
		redirect_url = auth.get_authorization_url()
		session['request_token'] = (auth.request_token.key, auth.request_token.secret)
		print session
	except tweepy.TweepError:
		'Authentication failure!'

	return flask.redirect(redirect_url)

@app.route('/verify')
def verify():
	verifier = request.args['oauth_verifier']
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	token = session['request_token']
	del session['request_token']

	auth.set_request_token(token[0], token[1])

	try:
		auth.get_access_token(verifier)
	except tweepy.TweepError:
		print "Auth failed!"
	
	api = tweepy.API(auth)

	db['api'] = api
	db['access_token_key'] = auth.access_token.key
	db['access_token_secret'] = auth.access_token.secret

	return flask.redirect(flask.url_for('controller'))

@app.route('/controller')
def controller():
	api = db['api']
	user = api.me()
	access = False

	if user.screen_name == 'truetone':
		access = True

	return render_template('controller.html', access=access)

if __name__ == '__main__':
	app.run(debug=True)

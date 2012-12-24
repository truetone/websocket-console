import flask, gevent, tweepy
import gevent.monkey
from gevent.pywsgi import WSGIServer

gevent.monkey.patch_all()

from flask import Flask, render_template, request, Response

consumer_key = "B6Ul7pUmm0OQYnoerqQ"
consumer_secret = "jLTZsgoDFH5hsNyxB5jkIkzbi23XhFQ2pMIEYWy2k"
callback_url = "http://localhost:5000/verify"
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

@app.route('/')
@app.route('/section/<section>')
def index(section=None):
	return render_template('index.html', section=section)

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
	
	api = tweepy.API

	db['api'] = api
	db['access_token_key'] = auth.access_token.key
	db['access_token_secret'] = auth.access_token.secret

	return flask.redirect(flask.url_for('controller'))

@app.route('/controller')
def controller():
	return render_template('controller.html')

if __name__ == '__main__':
	app.run(debug=True)

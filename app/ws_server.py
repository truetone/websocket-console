import sys
import config
import jsonpickle
import words
from random import choice
from twisted.python import log
from twisted.internet import reactor
from autobahn.websocket import WebSocketServerFactory, \
	WebSocketServerProtocol, \
	listenWS

def get_payload(message):
	return {
		'auth':		None,
		'data':		message,
	}

class Broadcast(WebSocketServerProtocol):
	""" Defines a connection to the WS server."""

	def __init__(self):
		self.admin = False

	def onConnect(self, request):
		print "+++++++++++++++++++++++++++++++++++++++++++"
		print "\nrequest: %s\n" % request
		print "+++++++++++++++++++++++++++++++++++++++++++"

		# Restrict to sections 1, 2 & 3?
		WebSocketServerProtocol.onConnect(self, request)
		if 'controller' in request.path:
			self.admin = True
			self.factory.register_admin(self)
		elif 'section' in request.path:
			section = int(request.path.split('section/')[1])
			self.word = choice(words.words)
			self.factory.register(self, section)
			# Send our session's request key to provide extremely basic message
			# signing from clients
			payload = get_payload(config.socket_key)
			payload['cmd'] = 'store'
			self.sendMessage(payload)

	def onMessage(self, msg, binary):
		if not binary:
			try:
				payload = jsonpickle.decode(msg)

				if not payload['cmd']:
					print "Received bad payload."
					return False
				else:
					print "Sending payload out.\n"
					print payload
					self.factory.broadcast_group(payload)
			except (RuntimeError, TypeError, NameError) as e:
				print e
				self.sendMessage('jsonpickle could not understand your data.')

			#if not payload['auth'] == config.socket_key:
			#	print "Recieved unauthorized request."

	def onOpen(self):
		payload = {}
		command = {}

		if self.admin:
			payload = get_payload(self.factory.clients)
			payload['cmd'] = 'updateclients'
			encoded_payload = jsonpickle.encode(payload)
			self.sendMessage(encoded_payload)

		else:
			try:
				#  {"cmd": {"chcolor": "red", "stn": "1"}}
				command['cmd'] = 'ft'
				command['val'] = choice(words.words)
				payload['cmd'] = command
				encoded_word = jsonpickle.encode(payload)
				print encoded_word
			except (RuntimeError, TypeError, NameError) as e:
				print e

			try:
				self.sendMessage(encoded_word)
				print "\nAttempted to send message to client.\n"

			except (RuntimeError, TypeError, NameError) as e:
				print e
				print "\nMessage could not be sent.\n"

	def connectionLost(self, reason):
		WebSocketServerProtocol.connectionLost(self, reason)
		self.factory.unregister(self)


class ServerFactory(WebSocketServerFactory):

	def __init__(self, url, debug=False, debugCodePaths=False):
		WebSocketServerFactory.__init__(self, url, debug=debug, debugCodePaths=debugCodePaths)
		self.last_client = 0
		self.clients = {}
		self.admins = []

	def register(self, client, section):

		print "||||||||||||||||||||||||||||||||||||||||||||||||||||"
		print "\n client: %s\n" % client
		print "||||||||||||||||||||||||||||||||||||||||||||||||||||"

		# See if the client is already in the group
		for group in self.clients:
			if client in self.clients[group]:
				return False

		# Check if the section exists in the dictionary; if not, initialize
		if not self.clients.get(section):
			self.clients.update({section: []})
		self.clients[section].append(client)

		payload = get_payload(self.clients)
		payload['cmd'] = 'updateclients'
		encoded_payload = jsonpickle.encode(payload)
		for admin in self.admins:
			admin.sendMessage(encoded_payload)
		print "Registered new client in section " + str(section) + "."

	def unregister(self, client):
		for group in self.clients:
			if client in self.clients[group]:
				self.clients[group].remove(client)

	def register_admin(self, admin):
		self.admins.append(admin)
		print "Registered new administrator!"

	def broadcast_all(self, message, cmd):
		payload = get_payload(message)
		payload['cmd'] = cmd
		for client in self.clients:
			client.sendMessage(jsonpickle.encode(payload))

	def broadcast_group(self, payload):
		print "broadcast_group received this payload:\n"
		print payload
		if 'cmd' in payload:
			#  {"cmd": {"chcolor": "red", "stn": "1"}}
			group = int(payload['cmd']['stn'])
			command = payload['cmd']['cmd']
			command_value = payload['cmd']['val']
			print "group: %s, command: %s, value: %s" % (group, command, command_value)
		else:
			print "Command not received.\n"
			
		print "Checking for group in self.clients.\n"

		for key in self.clients.keys():
			print "key: %s; group %s" % (key, group)
			print key == int(group)

		if group in self.clients.keys():
			print "\nWe found the group!\n"
			for client in self.clients[group]:
				client.sendMessage(jsonpickle.encode(payload))
				#client.sendMessage(jsonpickle.encode(payload))
		else:
			print "We couldn't find the group you're trying to signal."
			print "\nAre these the groups you're looking for?\n\n"
			print self.clients
			print "\n"


if __name__ == '__main__':
	factory = ServerFactory("ws://localhost:9000", debug=True, debugCodePaths=True)
	factory.protocol = Broadcast
	listenWS(factory)
	log.startLogging(sys.stdout)
	reactor.run()

import sys

import config

import jsonpickle
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


class EchoServerProtocol(WebSocketServerProtocol):
	""" Defines a connection to the WS server."""

	def __init__(self):
		self.admin = False

	def onMessage(self, msg, binary):
		# TODO: parse for console messages and commands
		if not binary:
			payload = jsonpickle.decode(msg)
			if not payload['cmd']:
				print "Received bad payload."
				return False
			if not payload['auth'] == config.socket_key:
				print "Recieved unauthorized request."

	def onConnect(self, request):
		WebSocketServerProtocol.onConnect(self, request)
		if 'controller' in request.path:
			self.admin = True
			self.factory.register_admin(self)
		elif 'section' in request.path:
			section = int(request.path.split('section/')[1])
			self.factory.register(self, section)
			# Send our session's request key to provide extremely basic message
			# signing from clients
			#payload = get_payload(config.socket_key)
			#payload['cmd'] = 'store'
			#self.sendMessage(payload)

	def onOpen(self):
		if self.admin:
			payload = get_payload(self.factory.clients)
			payload['cmd'] = 'updateclients'
			encoded_payload = jsonpickle.encode(payload)
			self.sendMessage(encoded_payload)

	def conncetionLost(self, reason):
		WebSocketServerProtocol.connectionLost(self, reason)
		self.factory.unregister(self)


class ServerFactory(WebSocketServerFactory):

	def __init__(self, url, debug=False, debugCodePaths=False):
		WebSocketServerFactory.__init__(self, url, debug=debug, debugCodePaths=debugCodePaths)
		self.last_client = 0
		self.clients = {}
		self.admins = []

	def register(self, client, section):
		print self.clients
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

	def broadcast_group(self, message, cmd, group):
		if group in self.clients.keys:
			payload = get_payload(message)
			payload['cmd'] = cmd
			for client in self.clients[group]:
				client.sendMessage(jsonpickle.encode(payload))


if __name__ == '__main__':
	factory = ServerFactory("ws://localhost:9000", debug=True, debugCodePaths=True)
	factory.protocol = EchoServerProtocol
	listenWS(factory)
	log.startLogging(sys.stdout)
	reactor.run()

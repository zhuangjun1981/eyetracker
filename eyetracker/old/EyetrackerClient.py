"""

@author: derricw

EyetrackerClient.py

Simple UDP client for communicating with Eyetracker/Recorder.

"""

import os
import socket

class Client(object):
	"""
	docstring for Eyetracker Client

	"""
	def __init__(self,
		incoming_ip='localhost',
		incoming_port=10000,
		outgoing_ip='localhost',
		outgoing_port=10001,
		output_filename=None):
		
		self.sock = socket.socket(socket.AF_INET,
			socket.SOCK_DGRAM)
		#self.sock.bind((incoming_ip,incoming_port))
		self.sock.settimeout(0.0)

		self.outgoing_ip = outgoing_ip
		self.outgoing_port = outgoing_port

		#Some users want to send a custom filename to the eyetracker
		if output_filename:
			self.output_filename = output_filename
		else:
			self.output_filename = ""

	def setup(self):
		pass

	def recordStart(self):
		self.sock.sendto("1"+self.output_filename,(self.outgoing_ip, self.outgoing_port))

	def recordStop(self):
		self.sock.sendto("0",(self.outgoing_ip, self.outgoing_port))

	def startStreaming(self):
		self.sock.sendto("2",(self.outgoing_ip, self.outgoing_port))

	def stopStreaming(self):
		self.sock.sendto("3",(self.outgoing_ip, self.outgoing_port))

	def getData(self):
		try:
			data,addr = self.sock.recvfrom(128)
		except:
			data = ""
		return data.strip()

if __name__ == '__main__':
	import time
	cl = Client()
	cl.recordStart()
	time.sleep(4)
	cl.recordStop()
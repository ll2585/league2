RIOT_API_KEY = ''
MASHAPE_API_KEY = ''
CONFIG_FILE = 'config.ini'

def apiKeys():
	return {'Riot': RIOT_API_KEY, 'Mashape': MASHAPE_API_KEY}

def writeConfigFile():
	import configparser
	config = configparser.ConfigParser()
	config['API Keys'] = {'Riot API Key': RIOT_API_KEY, 'Mashape API Key': MASHAPE_API_KEY}
	with open(CONFIG_FILE, 'w') as configfile:
		config.write(configfile)

def readConfigFile():
	import configparser
	config = configparser.ConfigParser()
	config.read(CONFIG_FILE)
	RIOT_API_KEY = config['API Keys']['Riot API Key']
	MASHAPE_API_KEY = config['API Keys']['Mashape API Key']
	config['API Keys'] = {'Riot API Key': RIOT_API_KEY, 'Mashape API Key': MASHAPE_API_KEY}

def saveAPIKeys(newKeys):
	RIOT_API_KEY = newKeys['RIOT_API_KEY']
	MASHAPE_API_KEY = newKeys['MASHAPE_API_KEY']
	writeConfigFile()

import os
if not os.path.exists(CONFIG_FILE):
	writeConfigFile()
else:
	readConfigFile()

import threading, time

class LogThread(threading.Thread):
	def run(self):
		TOTAL = 0
		for i in range(10000000):
			TOTAL = TOTAL + 1
			if TOTAL % 10000 == 0:
				print('%s' % (TOTAL))
				time.sleep(1)

class ServerThread(threading.Thread):
	def run(self):
		import server
		server.startServer()


def startRunning():
	logthread = LogThread()
	logthread.daemon = True
	logthread.start()
	serverThread = ServerThread()
	serverThread.daemon = True
	serverThread.start()

#Clock out word1 bit by bit on pin 19
#Data valid when clock (pin 23) goes from L to H
#Clock in 12 bits on pin 21
#Data valid when clock (pin 23) goes from L to H
#Work out decimal value based on position & value of bit
#X = position of bit
#Bit = 0 or 1
#Value = value of that bit
#anip = running total
#Print x, bit, value, anip
#Chip enable high
#Work out and print voltage

import sys
import RPi.GPIO as GPIO
import time
import datetime

import plotly.plotly as py
import json

from sys import argv
import os.path


def initGPIO():
	GPIO.setmode(GPIO.BOARD)

	GPIO.setup(24, GPIO.OUT)
	GPIO.setup(23, GPIO.OUT)
	GPIO.setup(19, GPIO.OUT)
	GPIO.setup(21, GPIO.IN)

	GPIO.output(24, True)
	GPIO.output(23, False)
	GPIO.output(19, True)

	GPIO.output(24, False)

def initPlotly():
	with open('./config.json') as config_file:
	    	plotly_user_config = json.load(config_file)

		py.sign_in(plotly_user_config["plotly_username"], plotly_user_config["plotly_api_key"])

		url = py.plot([
		{
			'x': [], 'y': [], 'type': 'scatter',
			'stream': {
			    'token': plotly_user_config['plotly_streaming_tokens'][0],
			    'maxpoints': 5000
			}
		    }], filename='hygro analog value', auto_open=False)

		print "View your streaming graph here: ", url
		stream = py.Stream(plotly_user_config['plotly_streaming_tokens'][0])
		stream.open()

		return stream

def endGPIO():
	GPIO.output(24, True)
	GPIO.cleanup()

def readAnalog():
	anip=0
	word1 = [1, 1, 1, 1, 1]
	for x in range (0,5):
		GPIO.output(19, word1[x])
		time.sleep(0.01)
		GPIO.output(23, True)
		time.sleep(0.01)
		GPIO.output(23, False)

	for x in range (0,12):
		GPIO.output(23,True)
		time.sleep(0.01)
		bit=GPIO.input(21)
		time.sleep(0.01)
		GPIO.output(23,False)
		value=bit*2**(12-x-1)
		anip=anip+value
	return anip


script, filename, streamit = argv

if os.path.isfile(filename):
	print "file already exists"
	sys.exit()

target = open(filename, 'w')
target.write("time, volts at custard\n")
initGPIO()
if int(streamit): 
	stream = initPlotly()
try:
	while True:	
		volt = readAnalog()*3.3/4096
		if int(streamit):
			stream.write({'x': datetime.datetime.now(), 'y': volt})
		x = datetime.datetime.now()
		print x, volt
		target.write(str(x) + "; " + str(volt) + "\n")
		time.sleep(1)
		
except KeyboardInterrupt:
	print "stopping"
	target.close()
	stream.close()
	endGPIO()
	sys.exit()

#TO TEST
#Connect Channel 0 to 3.3V and voltage should be 3.3V
#Connect two equal resistors in series from 3.3V to 0V.
#Connect mid point of resistors to Channel 0 input
#Voltage should be 1.65V


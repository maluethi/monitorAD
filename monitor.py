# author: matthias luethi
# Script to display A/D converted values from the custard pi 2 board on plot.ly. The script is basically a combination
# of two example scripts, namely (use these as reference):
#  - https://github.com/plotly/workshop/tree/master/raspberry-pi/tmp36
#  - http://www.sf-innovations.co.uk/downloads/cpi2_an_in.txt
#
# Usage: sudo python monitor.py OUTPUTFILE STREAMFLAG
# Issues: stream.close() seems to be very slow on the RPi

import sys
import RPi.GPIO as GPIO
import time
import datetime

import plotly.plotly as py
import json

from sys import argv
import os.path

# set GPIOs so they read A/D values
def initGPIO():
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(24, GPIO.OUT)
    GPIO.setup(23, GPIO.OUT)
    GPIO.setup(19, GPIO.OUT)
    GPIO.setup(21, GPIO.IN)

# clean up GPIO handling
def endGPIO():
    GPIO.output(24, True)
    GPIO.cleanup()

# use the json file for configuration, it should have this shape
# {
# "plotly_streaming_tokens": ["your_stream_token", "another_stream_token"],
# "plotly_api_key": "your_plotly_api_key",
# "plotly_username": "your_plotly_username"
# }
def initPlotly():
    with open('./config.json') as config_file:
        plotly_user_config = json.load(config_file)

        py.sign_in(plotly_user_config["plotly_username"], plotly_user_config["plotly_api_key"])

        url = py.plot([
                          {
                          'x': [], 'y': [], 'type': 'scatter',
                          'stream': {
                          'token': plotly_user_config['plotly_streaming_tokens'][0],
                          'maxpoints': 10000
                          }
                          }], filename='hygro analog value', auto_open=False)

        print "View your streaming graph here: ", url
        stream = py.Stream(plotly_user_config['plotly_streaming_tokens'][0])
        stream.open()

        return stream

# read the analog values
def readAnalog():

    GPIO.output(24, True)
    GPIO.output(23, False)
    GPIO.output(19, True)

    GPIO.output(24, False)
    anip = 0
    word1 = [1, 1, 1, 1, 1]
    for x in range(0, 5):
        GPIO.output(19, word1[x])
        time.sleep(0.01)
        GPIO.output(23, True)
        time.sleep(0.01)
        GPIO.output(23, False)

    for x in range(0, 12):
        GPIO.output(23, True)
        time.sleep(0.01)
        bit = GPIO.input(21)
        time.sleep(0.01)
        GPIO.output(23, False)
        value = bit * 2 ** (12 - x - 1)
        anip = anip + value
        #print x, bit, value, anip
    anip = anip * 3.3 / 4096
    return anip


def main():
    script, filename, streamit = sys.argv

    # configuration
    SampleInterval = 2 # in seconds

    # just protect yourself not to overwrite the data file
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
            volt = readAnalog()
            if int(streamit):
                stream.write({'x': datetime.datetime.now(), 'y': volt})
            x = datetime.datetime.now()
            print x, volt
            target.write(str(x) + "; " + str(volt) + "\n")
            time.sleep(SampleInterval)

    except KeyboardInterrupt:
        print "stopping"
        target.close()
        if int(streamit):
            stream.close()
        endGPIO()
        sys.exit()

if __name__ == "__main__":
    main()

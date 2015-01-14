#1/usr/bin/env python
#Sample Python code to test analogue inputs on Custard Pi 2
#www.sf-innovations.co.uk
#Program sets pins 24, 23 and 19 as outputs
#Pin 21 as input
#24 - chip enable
#23 - clock
#19 - data out
#21 - data in
#Word1
#1st bit High - start bit
#2nd bit High - two separate channels
#3rd bit High - input on Channel 1
#4th bit High - Most significant bit first
#5th bit High - Clock in null bit
#Chip enable (pin 24) Low
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


import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)

GPIO.setup(24, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(21, GPIO.IN)

GPIO.output(24, True)
GPIO.output(23, False)
GPIO.output(19, True)

word1= [1, 1, 1, 1, 1]

GPIO.output(24, False)
anip=0

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
    print x, bit, value, anip

GPIO.output(24, True)

volt = anip*3.3/4096
print volt

GPIO.cleanup()
import sys
sys.exit()

#TO TEST
#Connect Channel 0 to 3.3V and voltage should be 3.3V
#Connect two equal resistors in series from 3.3V to 0V.
#Connect mid point of resistors to Channel 0 input
#Voltage should be 1.65V

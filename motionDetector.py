import argparse
import RPi.GPIO as GPIO
import time
import signal
import sys

SIGNAL_DURATION = 4
MIN_TIME = 8

inputPin = 15
outputPin = 16
outputFileName = "motion.state"

# Arguments

parser = argparse.ArgumentParser(description=
  '''
Driver for motion detector, LED indicator and writer to file.
Detector signal must be connected to BCM pin %d and output to pin %d.
State is written to file "%s"''' % (inputPin, outputPin, outputFileName)
)
parser.add_argument('-t', type=int, default=10, help='seconds, how long LED will light, at least %d' % MIN_TIME)
parser.add_argument('-d', type=float, default=0.3, help='seconds, delay between updates of the state')
parser.add_argument('-p', action='store_true', help='Print to console state change')

args = parser.parse_args()

if args.t < MIN_TIME:
	print "Light up time must not be shorter than 8 seconds."
	exit(1)
if args.d < 0.1:
	print "Delay too small"
	exit(2)

# Prepare handling  Ctrl+C

def signal_handler(sig, frame):
        print "\nCleaning up GPIO"
	GPIO.cleanup()
	print "Done"
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Init GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(outputPin, GPIO.OUT)
GPIO.setup(inputPin, GPIO.IN)

# Motion detection

print "\nStop by Ctrl+C\n"

delay = args.t

trueState = 0
sinceOff = 0
delayTime = args.d
updateDelay = delay - SIGNAL_DURATION

def updateFile():
	global trueState
	file = open(outputFileName, "w")
	file.write("%d" % trueState)
	file.close()

while 1:
	state = GPIO.input(inputPin)
	if not state:
		if trueState:
			if (sinceOff >= updateDelay):
				trueState = 0
				if args.p:
					print "Off"
				GPIO.output(outputPin, GPIO.LOW)
				updateFile()
			else:
				sinceOff += delayTime
	elif not trueState:
		GPIO.output(outputPin, GPIO.HIGH)
		sinceOff = 0
		if args.p:
			print "On"
		trueState = 1
		updateFile()
	time.sleep(0.3)


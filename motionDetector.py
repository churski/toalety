import argparse
#import RPi.GPIO as GPIO
import gpioMock as GPIO
import time
import signal
import sys

SIGNAL_DURATION = 4
MIN_TIME = 8

signalPinMale = 15
diodePinMale = 16
signalPinFemale = 23
diodePinFemale = 12
outputFileName = "motion.state"

# Arguments

parser = argparse.ArgumentParser(description=
'''
Driver for motion detector, LED indicator and writer to file.
'''
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

class SensorData:
    def __init__(self, signalPin, diodePin):
            self.trueState = 0
            self.sinceOff = 0
            self.delayTime = args.d
            self.updateDelay = delay - SIGNAL_DURATION
            self.signalPin = signalPin
            self.diodePin = diodePin
    

def updateFile(sensors):
    global trueState
    file = open(outputFileName, "w")
    for sensor in sensors:
        file.write("%d\n" % sensor.trueState)
    file.close()

def updateState(sensor):
    change = false
    state = GPIO.input(sensor.signalPin)
    if not state:
        if sensor.trueState:
            if (sensor.sinceOff >= sensor.updateDelay):
                sensor.trueState = 0
                if args.p:
                    print "Off"
                GPIO.output(sensor.diodePin, GPIO.LOW)
                change = true
            else:
                sensor.sinceOff += delayTime
    elif not sensor.trueState:
        GPIO.output(sensor.diodePin, GPIO.HIGH)
        sensor.sinceOff = 0
        if args.p:
            print "On"
        sensor.trueState = 1
        change = true
    return change

maleSensor = SensorData(
    signalPinMale,
    diodePinMale
)
femaleSensor = SensorData(
    signalPinFemale,
    diodePinFemale
)

while 1:
    change = false
    change = change or updateSensor(maleSensor)
    change = change or updateSensor(femaleSensor)
    if change:
        updateFile([maleSensor, femaleSensor])
    time.sleep(0.3)

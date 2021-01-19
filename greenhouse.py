import RPi.GPIO as GPIO
import Adafruit_DHT
import datetime as dt
#from MCP3008 import MCP3008
from gpiozero import MCP3008
import time

##################################################################
##################### CUSTOMIZEABLE SETTINGS #####################
##################################################################
SETTINGS = {
    "LIGHT_GPIO":       17,                     # GPIO Number (BCM) for the Relay
    "LIGHT_FROM":       10,                     # from which time the light can be turned on (hour)
    "LIGHT_UNTIL":      23,                     # until which time (hour)
    "LIGHT_CHANNEL":    0,                      # of MCP3008
    "LIGHT_THRESHOLD":  500,                    # if the analog Threshold is below any of those, the light will turn on (this was 500 units of what ever)
    "DHT_GPIO":         27,                     # GPIO Number (BCM) of the DHT Sensor
    "DHT_SENSOR":       Adafruit_DHT.DHT22,     # DHT11 or DHT22
    "TEMP_THRESHOLD":   23.0,                   # in Celcius. Above this value, the window will be opened by the servo
    "SERVO_GPIO":       22,                     # GPIO Number (BCM), which opens the window
    "SERVO_OPEN_ANGLE": 90.0,                   # degree, how much the servo will open the window
    "PLANTS": [
        {
            "NAME":                 "Tomaten",
            "MOISTURE_CHANNELS":    [1,2],     # of MCP3008
            "MOISTURE_THRESHOLD":   250,        # if the average analog value of all sensors is above of this threshold, the Pump will turn on
            "WATER_PUMP_GPIO":      24,         # GPIO Number (BCM) for the Relais
            "WATERING_TIME":        10,         # Seconds, how long the pump should be turned on
        },
     ]
}
##################################################################
################# END OF CUSTOMIZEABLE SETTINGS ##################
##################################################################

def readTime():
    try:
	print "Got to the timestamp"
	print dt.datetime.today().hour
	return dt.datetime.today().hour
    except:
        # alternative: return the system-time:
        return 0

def checkLight():
    timestamp = readTime()
    print "Got to the check Light"

    if SETTINGS["LIGHT_FROM"] <= timestamp <= SETTINGS["LIGHT_UNTIL"]:

        # check light sensors
        adc = MCP3008(channel= SETTINGS["LIGHT_CHANNEL"])
        # read 10 times to avoid measuring errors
        value = 0
        for i in range(10):
            value += adc.value
            #value += adc.read( channel = SETTINGS["LIGHT_CHANNEL"] )
        value /= 10.0
        print "I got to the light section and the value is " 
        print(value)

        if value <= SETTINGS["LIGHT_THRESHOLD"]:
            # turn light on
            GPIO.setup(SETTINGS["LIGHT_GPIO"], GPIO.OUT, initial=GPIO.LOW) # Relay LOW = ON
	    print "I guess I should turn on the light, right?"
        else:
            # turn light off
            GPIO.setup(SETTINGS["LIGHT_GPIO"], GPIO.OUT, initial=GPIO.HIGH)
	    print "I turned off the light because the value is above threshold"
    else:
        # turn light off
        GPIO.setup(SETTINGS["LIGHT_GPIO"], GPIO.OUT, initial=GPIO.HIGH)
	print "I turned the light off because it is not the time"

def wateringPlants():
    # read moisture
    for plantObject in SETTINGS["PLANTS"]:
        value = 0
        for ch in plantObject["MOISTURE_CHANNELS"]:
            adc = MCP3008(channel = ch)
            # read 10 times to avoid measuring errors
            v = 0
            for i in range(10):
                v += adc.value
            v /= 10.0
            value += v
            print ("I got to the channel nr",ch)
            print value 
        value /= float(len(plantObject["MOISTURE_CHANNELS"]))
        print ("I got to the sum of channels, the new value is",value)
	
        if value >= 0: #plantObject["MOISTURE_THRESHOLD"]:
	    print "I found that the value is too low so I' going to turn on the pump"
            # turn pump on for some seconds
            GPIO.setup(plantObject["WATER_PUMP_GPIO"], GPIO.OUT, initial=GPIO.LOW)
            time.sleep(plantObject["WATERING_TIME"])
            GPIO.output(plantObject["WATER_PUMP_GPIO"], GPIO.HIGH)


if __name__ == '__main__':
    try:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        # execute functions
        checkLight()
        wateringPlants()
    except:
        GPIO.cleanup()

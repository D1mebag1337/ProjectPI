#              .';:cc;.
#            .,',;lol::c.
#            ;';lddddlclo
#            lcloxxoddodxdool:,.
#            cxdddxdodxdkOkkkkkkkd:.
#          .ldxkkOOOOkkOO000Okkxkkkkx:.
#        .lddxkkOkOOO0OOO0000Okxxxxkkkk:
#       'ooddkkkxxkO0000KK00Okxdoodxkkkko
#      .ooodxkkxxxOO000kkkO0KOxolooxkkxxkl
#      lolodxkkxxkOx,.      .lkdolodkkxxxO.
#      doloodxkkkOk           ....   .,cxO;
#      ddoodddxkkkk:         ,oxxxkOdc'..o'
#      :kdddxxxxd,  ,lolccldxxxkkOOOkkkko,
#       lOkxkkk;  :xkkkkkkkkOOO000OOkkOOk.
#        ;00Ok' 'O000OO0000000000OOOO0Od.
#         .l0l.;OOO000000OOOOOO000000x,
#            .'OKKKK00000000000000kc.
#               .:ox0KKKKKKK0kdc,.
#                      ...
#
# Author: peppe8o
# Date: May 5th, 2020
# Version: 1.0

# Import required libraries
import sys
import RPi.GPIO as GPIO
import Adafruit_DHT
import time

######### GPIO setup ##########

# Use BCM GPIO references instead of physical pin numbers
GPIO.setmode(GPIO.BCM)

# Temperatursensor
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

# Bodenfeuchtigkeitssensor
data = 21
green = 6
red = 19

GPIO.setmode(GPIO.BCM)
GPIO.setup(data, GPIO.IN)
GPIO.setup(red, GPIO.OUT)
GPIO.setup(green, GPIO.OUT)

GPIO.output(green,GPIO.LOW)
GPIO.output(red,GPIO.LOW)

# Sieben-Segment-Anzeige

delay = 0.0005 # delay between digits refresh

# --------------------------------------------------------------------
# PINS MAPPING AND SETUP
# selDigit activates the 4 digits to be showed (0 is active, 1 is unactive)
# display_list maps segments to be activated to display a specific number inside the digit
# digitDP activates Dot led
# --------------------------------------------------------------------

selDigit = [14,15,18,23]
# Digits:   1, 2, 3, 4

display_list = [24,25,10,9,26,12,16] # define GPIO ports to use
#disp.List ref: A ,B ,C,D,E,F ,G

digitDP = 20
#DOT = GPIO 20

# Set all pins as output
GPIO.setwarnings(False)
for pin in display_list:
  GPIO.setup(pin,GPIO.OUT) # setting pins for segments
for pin in selDigit:
  GPIO.setup(pin,GPIO.OUT) # setting pins for digit selector
GPIO.setup(digitDP,GPIO.OUT) # setting dot pin
GPIO.setwarnings(True)

# DIGIT map as array of array ,
#so that arrSeg[0] shows 0, arrSeg[1] shows 1, etc
arrSeg = [[0,0,0,0,0,0,1],\
          [1,0,0,1,1,1,1],\
          [0,0,1,0,0,1,0],\
          [0,0,0,0,1,1,0],\
          [1,0,0,1,1,0,0],\
          [0,1,0,0,1,0,0],\
          [0,1,0,0,0,0,0],\
          [0,0,0,1,1,1,1],\
          [0,0,0,0,0,0,0],\
          [0,0,0,0,1,0,0],\
	        [0,0,1,1,1,0,0],\
	        [0,1,1,0,0,0,1]]

GPIO.output(digitDP,0) # DOT pin

# --------------------------------------------------------------------
# MAIN FUNCTIONS
# splitToDisplay(string) split a string containing numbers and dots in
#   an array to be showed
# showDisplay(array) activates DIGITS according to array. An array
#   element to space means digit deactivation
# --------------------------------------------------------------------
def getTemperature():
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
      temperature = str(round(temperature)) + "°C"
    else:
        temperature = "0000"
    return temperature

def getMoistureData():
    if GPIO.input(data):
        GPIO.output(green, GPIO.LOW) #bei keinem Wasser geht Grün aus
        GPIO.output(red, GPIO.HIGH) #und Rot leuchtet
    else:
        GPIO.output(green, GPIO.HIGH) #bei Wasser geht Grün an
        GPIO.output(red, GPIO.LOW) #und Rot geht aus

def showDisplay(digit):
 for i in range(0, 4): #loop on 4 digits selectors (from 0 to 3 included)
  sel = [0,0,0,0]
  sel[i] = 1
  GPIO.output(selDigit, sel) # activates selected digit
  if digit[i].replace(".", "") == " ": # space disables digit
   GPIO.output(display_list,0)
   continue
  if digit[i] == "°":
   GPIO.output(display_list,arrSeg[10])
   time.sleep(delay)
   continue
  if digit[i] == "C":
   GPIO.output(display_list,arrSeg[11])
   time.sleep(delay)
   continue
  numDisplay = int(digit[i].replace(".", ""))
  GPIO.output(display_list, arrSeg[numDisplay]) # segments are activated according to digit mapping
  if digit[i].count(".") == 1:
   GPIO.output(digitDP,0)
  else:
   GPIO.output(digitDP,1)
  time.sleep(delay)

def splitToDisplay (toDisplay): # splits string to digits to display
 arrToDisplay=list(toDisplay)
 for i in range(len(arrToDisplay)):
  if arrToDisplay[i] == ".": arrToDisplay[(i-1)] = arrToDisplay[(i-1)] + arrToDisplay[i] # dots are concatenated to previous array element
 while "." in arrToDisplay: arrToDisplay.remove(".") # array items containing dot char alone are removed
 return arrToDisplay


# --------------------------------------------------------------------
# MAIN LOOP
# persistence of vision principle requires that digits are powered
#   on and off at a specific speed. So main loop continuously calls
#   showDisplay function in an infinite loop to let it appear as
#   stable numbers display
# --------------------------------------------------------------------

try:
  while True:
    GPIO.output(selDigit, [0,0,0,0])
    t_end = time.time() + 10
    toDisplay = getTemperature()
    while time.time() < t_end:
      getMoistureData()
      showDisplay(splitToDisplay(toDisplay)) 
except KeyboardInterrupt:
  print('interrupted!')
  GPIO.output(selDigit, [0,0,0,0])
  GPIO.cleanup()
sys.exit()


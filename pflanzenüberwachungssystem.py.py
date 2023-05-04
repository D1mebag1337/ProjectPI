# Importieren der benötigten Bibliotheken
import sys
import RPi.GPIO as GPIO
import Adafruit_DHT
import time

######### GPIO setup ##########

# Benutzen der Pin Namen statt ihrer physischen Anordnung
GPIO.setmode(GPIO.BCM)

# Temperatursensor
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

# Bodenfeuchtigkeitssensor
data = 21
green = 6
red = 19

GPIO.setup(data, GPIO.IN)
GPIO.setup(red, GPIO.OUT)
GPIO.setup(green, GPIO.OUT)

GPIO.output(green,GPIO.LOW)
GPIO.output(red,GPIO.LOW)

# Sieben-Segment-Anzeige

delay = 0.0005 # Zeitverzögerung zwischen den einzelnen Ziffern

# Ziffern:   1, 2, 3, 4
selDigit = [14,15,18,23]

#Segmente: A ,B ,C ,D ,E ,F ,G
display_list = [24,25,10,9,26,12,16]

#Punkt = GPIO 20
digitDP = 20


# Setze all Pins als Output
GPIO.setwarnings(False)
for pin in display_list:
  GPIO.setup(pin,GPIO.OUT) # setzen der Pins für die Segmente
for pin in selDigit:
  GPIO.setup(pin,GPIO.OUT) # setzen der Pins für die Ziffern
GPIO.setup(digitDP,GPIO.OUT) # 
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

GPIO.output(digitDP,0) # Punkt aus


######## Funktionen ########

# Auslesen des Temperatursensors
def getTemperature():
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN) #Temperatur auslesen
    if humidity is not None and temperature is not None:
      temperature = str(round(temperature)) + "°C" #Aufrunden der Temperatur und verknüpfen mit '°C'
    else:
        temperature = "0000" #bei keinem Signal alles auf 0
    return temperature

# Auslesen des Bodenfeuchtigkeitssensors und steuern der LED
def getMoistureData():
    if GPIO.input(data):
        GPIO.output(green, GPIO.LOW) #bei keinem Wasser geht Grün aus
        GPIO.output(red, GPIO.HIGH) #und Rot leuchtet
    else:
        GPIO.output(green, GPIO.HIGH) #bei Wasser geht Grün an
        GPIO.output(red, GPIO.LOW) #und Rot geht aus

# Aktiviert die Segmente entsprechend der übergebenen Zahl
def showDisplay(digit):
 for i in range(0, 4): #Schleifendurchlauf für alle Ziffern
  sel = [0,0,0,0]
  sel[i] = 1
  GPIO.output(selDigit, sel) #aktivieren der ausgewählten Ziffer
  if digit[i].replace(".", "") == " ": #Leerzeichen deaktiviert die Ziffer
   GPIO.output(display_list,0)
   continue
  if digit[i] == "°":
   GPIO.output(display_list,arrSeg[10]) #bei Grad-Zeichen wird der Index 10 angesprochen
   time.sleep(delay)
   continue
  if digit[i] == "C":
   GPIO.output(display_list,arrSeg[11]) #bei C wird Index 11 angesprochen
   time.sleep(delay)
   continue
  numDisplay = int(digit[i].replace(".", ""))
  GPIO.output(display_list, arrSeg[numDisplay]) # die Segmente werden dementsprechenden Mapping angeschaltet
  if digit[i].count(".") == 1:
   GPIO.output(digitDP,0)
  else:
   GPIO.output(digitDP,1)
  time.sleep(delay)

# Aufbereiten der übergebenen Werte indem der String geteilt wird
def splitToDisplay (toDisplay):
 arrToDisplay=list(toDisplay)
 for i in range(len(arrToDisplay)):
  if arrToDisplay[i] == ".": arrToDisplay[(i-1)] = arrToDisplay[(i-1)] + arrToDisplay[i] # Punkte werden mit dem vorigen Element verknüpft
 while "." in arrToDisplay: arrToDisplay.remove(".") # Array Elemente mit Punkt werden gelöscht
 return arrToDisplay



######## MAIN LOOP ########

try:
  while True:
    GPIO.output(selDigit, [0,0,0,0]) 
    t_end = time.time() + 10 #definieren des Zeitintervalls zum Temperatur-Refresh
    toDisplay = getTemperature()
    while time.time() < t_end:
      getMoistureData()
      showDisplay(splitToDisplay(toDisplay)) 
except KeyboardInterrupt:
  print('interrupted!')
  GPIO.output(selDigit, [0,0,0,0])
  GPIO.cleanup()
sys.exit()


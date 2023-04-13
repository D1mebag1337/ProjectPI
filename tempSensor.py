import time

#Einlesen der Datei
file = open('/sys/bus/w1/devices/28-3c01a816491d/w1_slave')
#Datastream oeffnen
temp = file.read()
file.close()

index = temp.find("t=")+2
newTemp = float(temp[index:])
newTemp = newTemp/1000

print("Die vom Sensor gemessene Temperatur ist:",round(newTemp,2),"Grad C")

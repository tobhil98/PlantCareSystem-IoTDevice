#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import ssl
import smbus
import math
from time import sleep
import gpiozero
import json
from multiprocessing import Process, Queue
from datetime import datetime
from uuid import getnode as get_mac

savedSettings = "settings/settings.json"
ourMQTT = "IC.embedded/obedient_fighting_snakes/"
cert = ["certificates/mosquitto.org.crt","certificates/client.crt","certificates/client.key"]
decNbrs = 1

pumpPin = 24
pump = gpiozero.DigitalOutputDevice(pumpPin)
bus = smbus.SMBus(1)
measurements = Queue()

#automatic watering configuration
readingFrequency = None
automaticWaterTime = None
moistureThreshold = None
auto_water = None
waterSleep = 120 #minutes

#create mqtt clients
receiver = mqtt.Client(userdata=["reciever",ourMQTT, bus, pump]) #pass all the data needed inside callbacks. remember that those are pointers.
sender = mqtt.Client(userdata=["sender"]) #sends to ourMQTT/measurementRead thread
#sender configuration
updateProxyTimer = 10 #seconds

#I/O functionality
def getMoistureReading(bus):
    adcAddr = 0x48
    convReg = 0x0
    confReg = 0x1
    #write to config register
    bus.write_word_data(adcAddr,confReg, 0b1000010010000011)
    sleep(0.01)
    #write to conv register
    bus.write_byte_data(adcAddr, convReg, 0)
    sleep(0.01)
    #read data from conv register

    measurement = bus.read_i2c_block_data(adcAddr, convReg, 2)
    if (measurement == [127,255]):
        raise Exception('Sensor out of soil')

    relative = int.from_bytes(measurement,'big')
    moisturePercentage = 100 * relative / 65536.0

    return round(moisturePercentage, decNbrs)

def getTempHumidReading(bus):
    rawTemp = bus.read_i2c_block_data(0x40,0xE3,2)
    sleep(0.01)
    rawHumid = bus.read_i2c_block_data(0x40,0xE5,2)
    sleep(0.01)
    temp  = 175.72*(rawTemp[0]<<8 | rawTemp[1])/65536.0 - 46.85
    humid = 125*(rawHumid[0]<<8 | rawHumid[1])/65536.0 - 6.0
    return round(temp,decNbrs), round(humid,decNbrs)

def runPump(pump, time):
    pump.on()
    sleep(time)
    pump.off()
    print("finished pumping water")

#helper functions
def packAllMeasurements(t, h, m):
    now = datetime.now()
    dataOut = {
        "date": now.strftime("%d/%m/%Y"),
        "time": now.strftime("%H:%M"),
        "temp": t,
        "humid": h,
        "moist": m,
        "id": get_mac() #mac address as 48bit integer
    }
    return json.dumps(dataOut)

def packLastWatered():
    now = datetime.now()
    dataOut = {
        "date": now.strftime("%d/%m/%Y"),
        "time": now.strftime("%H:%M"),
        "id": get_mac() #mac address as 48bit integer
    }
    return json.dumps(dataOut)

def unpackSettings(inString):
    inData = json.loads(inString)
    return [inData['readin_freq'], inData['water_duration'], inData['moisture_threshold'], inData['auto_water']]

#MQTT callbacks
def on_message(client, userdata, msg):
    print("entered wrong callback")

def on_connect(client, userdata, flags, rc):
    if (rc == 0):
        now = datetime.now()
        print(userdata[0], "sucessfully connected to server at", now.strftime("%d/%m/%Y %H:%M:%S"))

def mesasurementCallback(client, userdata, msg):
    bus = userdata[2]
    ourMQTT = userdata[1]

    temp, humid = getTempHumidReading(bus)
    try:
        moist = getMoistureReading(bus)
    except:
        moist = 0.0

    dataOut = packAllMeasurements(temp, humid, moist)
    measurements.put(dataOut) #put the data into queue

def pumpCallback(client, userdata, msg):
    pump = userdata[3]
    try:
        pumpThread = Process(target = runPump, args=(pump, automaticWaterTime))
        pumpThread.start()
        measurements.put(packLastWatered())
    except:
        pump.off()
        print("pump turned off")

def settingsCallback(client, userdata, msg):
    message = str(msg.payload)[2:-1]
    with open(savedSettings,"w") as file:
        file.write(message)
    settings = unpackSettings(message)
    readingFrequency = settings[0] * 60
    automaticWaterTime = settings[1]
    moistureThreshold = settings[2]
    auto_water = settings[3]

#SelfFlower functionality
def automaticWatering():
    while True:
        sleep(readingFrequency)
        try:
            if(not auto_water):
                continue
            moist = getMoistureReading(bus)
            if(moist < (moistureThreshold+1)*20):

                pumpThread = Process(target = runPump, args=(pump, automaticWaterTime))
                pumpThread.start()
                sleep(waterSleep * 60)
        except:
            pass

def automaticMeasurement():
    while True:
        temp, humid = getTempHumidReading(bus)
        try: #automatic update
            moist = getMoistureReading(bus)
            dataOut = packAllMeasurements(temp, humid, moist)
        except:
            dataOut = packAllMeasurements(temp, humid, 0.0)
            #pass #uncomment in order not to send messages
        measurements.put(dataOut)

        sleep(readingFrequency)

def updateStatus(client):
    dest = ourMQTT + "measurementRead"
    client.loop_start()
    msgCount = 0
    while True:
        while True: #send contents of queue to mqtt broker
            try:
                msg = measurements.get_nowait()
                client.publish(dest, msg, qos=2)
                sleep(0.1)
                msgCount += 1
            except:
                if(msgCount):
                    print(msgCount, "messages have been sent to",dest)
                    msgCount = 0
                break
        sleep(updateProxyTimer)

if __name__ == "__main__":
    receiver.tls_set(ca_certs=cert[0], certfile=cert[1],keyfile=cert[2],tls_version=ssl.PROTOCOL_TLSv1_2)
    receiver.connect("test.mosquitto.org",8884)
    receiver.subscribe(ourMQTT + "measurementRequest")
    receiver.subscribe(ourMQTT + "pumpRequest")
    receiver.subscribe(ourMQTT + "settings")

    sender.tls_set(ca_certs=cert[0], certfile=cert[1],keyfile=cert[2],tls_version=ssl.PROTOCOL_TLSv1_2)
    sender.connect("test.mosquitto.org",8884)

    #update settings on startup
    with open(savedSettings) as file:
        settings = unpackSettings(file.read())
        readingFrequency = settings[0] * 60
        automaticWaterTime = settings[1]
        moistureThreshold = settings[2]
        auto_water = settings[3]
        print("Data",settings)

    #configure sender and reciever
    receiver.on_message = on_message
    receiver.on_connect = on_connect
    receiver.message_callback_add(ourMQTT + "measurementRequest", mesasurementCallback)
    receiver.message_callback_add(ourMQTT + "pumpRequest", pumpCallback)
    receiver.message_callback_add(ourMQTT + "settings", settingsCallback)
    sender.on_message = on_message
    sender.on_connect = on_connect

    #open threads for SelfFlower functionality
    try:
        receiver.loop_start()
        watering = Process(target = automaticWatering)
        watering.start()
        measurement = Process(target = automaticMeasurement)
        measurement.start()
        mqttUpdate = Process(target = updateStatus, args=(sender,))
        mqttUpdate.start()
    except:
        receiver.loop_stop()
        sender.loop_stop()
        pump.off()

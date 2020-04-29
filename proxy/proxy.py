#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import ssl
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import threading
import json
from multiprocessing import Process, Queue
from time import sleep

#parameters
updateDB = True
updateDBTimer = 5
dataSheet = "PlantPot_data"
ourMQTT = "IC.embedded/obedient_fighting_snakes/"

#google api magic
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
cert = ['certificates/client_secret.json', "certificates/mosquitto.org.crt",
        "certificates/client.crt","certificates/client.key"]
creds = ServiceAccountCredentials.from_json_keyfile_name(cert[0], scope)
gsheets = gspread.authorize(creds)

sheet = gsheets.open(dataSheet)
worksheetList = sheet.worksheets()

data = worksheetList[0]
settings = worksheetList[1]

measurements = Queue()


#create mqtt client
client = mqtt.Client(userdata=[updateDB, ourMQTT]) #pass all the data needed inside callbacks. remember that those are pointers.
client.tls_set(ca_certs=cert[1], certfile=cert[2],keyfile=cert[3],tls_version=ssl.PROTOCOL_TLSv1_2)
client.connect("test.mosquitto.org",8884)

#helper functions
def sendMessage(client, topic, msg):
    dest = ourMQTT + topic
    client.publish(dest, msg, qos=2)
    print(msg, "sent to", topic)

def unpackData (inString):
    inData = json.loads(inString)
    if(len(inData) == 6):
        return [inData['date'], inData['time'], inData['temp'], inData['humid'], inData['moist']]
    elif(len(inData) == 3):
        return [inData['date'], inData['time']]
    else:
        return []
#client callbacks
def on_message(client, userdata, msg):
    print("entered wrong callback")

def on_connect(client, userdata, flags, rc):
    if (rc == 0):
        print("Sucessfully connected to server")
        ourMQTT = userdata[1]
        client.subscribe(ourMQTT + "measurementRead")
        client.subscribe(ourMQTT + "return")

def measurementCallback(client, userdata, msg):
    updateDB = userdata[0]
    newInfo = unpackData(str(msg.payload)[2:-1])
    if updateDB:
        measurements.put(newInfo)
    else:
        print(newRow, "has been recieved and not added")

def return_callback(client, userdata, msg):
    nbr = re.findall(r"[\d]+", str(msg.payload))[0]
    package = "Return message with value " + nbr
    sendMessage(client, "testReturn", package)
    #userdata[0] += 1

#main:
client.on_message = on_message
client.on_connect = on_connect
client.message_callback_add(ourMQTT + "measurementRead", measurementCallback)
client.message_callback_add(ourMQTT + "return", return_callback)

#run background routines here

def recieveMessage():
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        client.loop_stop()
        print("finished execution")

def dbHandler():
    global measurements
    settingsClient = mqtt.Client(userdata=[updateDB, ourMQTT])
    settingsClient.tls_set(ca_certs=cert[1], certfile=cert[2],keyfile=cert[3],tls_version=ssl.PROTOCOL_TLSv1_2)
    settingsClient.connect("test.mosquitto.org",8884)
    readin_freq = 0
    water_duration = 0
    moisture_threshold = 0
    auto_water = 0
    settingsClient.loop_start()

    while True:
        if creds.access_token_expired:
            gsheets.login()  # refreshes the token

        #settings update
        prev_readin_freq = readin_freq
        prev_water_duration = water_duration
        prev_moisture_threshold = moisture_threshold
        prev_auto_water = auto_water

        readin_freq = int(settings.cell(3, 2).value)
        water_duration = int(settings.cell(4, 2).value)
        moisture_threshold = int(settings.cell(5, 2).value)
        auto_water = int(settings.cell(6, 2).value)

        if(prev_readin_freq != readin_freq or prev_water_duration != water_duration or prev_moisture_threshold != moisture_threshold or prev_auto_water != auto_water):
            dataOut = {
                "readin_freq": readin_freq,
                "water_duration": water_duration,
                "moisture_threshold": moisture_threshold,
                "auto_water": auto_water
            }
            jsonData = json.dumps(dataOut)
            sendMessage(settingsClient, "settings", jsonData)

        #water
        if(int(settings.cell(2, 2).value)):
            settings.update_cell(2, 2, 0)
            sendMessage(settingsClient, "pumpRequest", "request")

        if not updateDB:
            continue

        while True:
            try:
                m = measurements.get_nowait()
                if(len(m) == 5):
                    data.insert_row(m, 2, value_input_option='USER_ENTERED')
                    print(m, "has been added to database")
                elif(len(m) == 2):
                    settings.update_cell(9, 2, m[0])
                    settings.update_cell(8, 2, m[1])
                    print("last watered reading has been updated to", m)
                else:
                    print("strange things happen to people")
            except:
                break

        sleep(updateDBTimer)

if __name__ == "__main__":
    p1 = Process(target = recieveMessage)
    p1.start()
    p2 = Process(target = dbHandler)
    p2.start()

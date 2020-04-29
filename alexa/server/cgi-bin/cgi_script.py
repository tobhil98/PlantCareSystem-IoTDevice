#!/usr/bin/env python3

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import sys
from os import system

#google api magic
dataSheet = "PlantPot_data"
fn = '/home/pi/cgi-bin/iot_settings.txt'
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
cert = '/home/pi/cgi-bin/certificates/client_secret.json'
creds = ServiceAccountCredentials.from_json_keyfile_name(cert, scope)
gsheets = gspread.authorize(creds)
sheet = gsheets.open(dataSheet)

worksheetList = sheet.worksheets()
settings = worksheetList[1]

#extract alexa message
bracketCounter = 0
alexaInput = []
firstRun = True
while True:
    c = sys.stdin.read(1)
    if(c == '{'):
        bracketCounter += 1
    elif(c == '}'):
        bracketCounter -=1
    alexaInput.append(c)
    if(not firstRun and bracketCounter == 0):
        break
    firstRun = False

alexaInput = json.loads(''.join(alexaInput))
name = alexaInput['request']['intent']['name']

if name == "pump":
    status = alexaInput['request']['intent']['slots']['status']['value']

#start alexa response
print("Cache-Control: no-cache, no-store, must-revalidate",flush=True)
print("Pragma: no-cache",flush = True)
print("Expires: 0", flush=True)
print("Content-Type: application/json;charset=UTF-8",flush=True)
print("",flush=True)

if name == "water_plant" :
    #write to file to water
    settings.update_cell(2, 2, 1)
    print( "{ \"version\": \"1.0\", \"response\": { \"outputSpeech\": { \"type\": \"PlainText\", \"text\": \"Watering your plant now..\"} }}", flush=True)
    
elif name == "last_watered":
    date = settings.cell(11,2).value
    #read from last watered file
    print( "{ \"version\": \"1.0\", \"response\": { \"outputSpeech\": { \"type\": \"PlainText\", \"text\": \"Your plant was last watered on " + date +" \"} }}", flush=True)
    
elif name == "pump":
    #write 1/0 to file based on status
    print( "{ \"version\": \"1.0\", \"response\": { \"outputSpeech\": { \"type\": \"PlainText\", \"text\": \"Got it. Turning automatic watering "+status+".\"} }}", flush=True)
    settings.update_cell(6, 2, "1" if status == "on" else "0")
elif name == "AMAZON.HelpIntent":
    print("{ \"version\": \"1.0\", \"response\": { \"outputSpeech\": { \"type\": \"PlainText\", \"text\": \" You can try asking your flower to water your plant or when it was last watered. He can also change your watering settings. Just try saying, ask my flower to turn automatic watering on. \"} } }")
elif name == "online":
    if settings.cell(10,2).value == "1":
        print( "{ \"version\": \"1.0\", \"response\": { \"outputSpeech\": { \"type\": \"PlainText\", \"text\": \"Your plant is online\"} }}", flush=True)
    else:
        print( "{ \"version\": \"1.0\", \"response\": { \"outputSpeech\": { \"type\": \"PlainText\", \"text\": \"Your plant is no longer online. Try checking your internet connection.\"} }}", flush=True)
     
else:
    print( "{ \"version\": \"1.0\", \"response\": { \"outputSpeech\": { \"type\": \"PlainText\", \"text\": \"Try asking your plant for help \"} }}", flush=True)


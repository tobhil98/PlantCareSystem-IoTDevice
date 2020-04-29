## Client - Moist.py

- The program will launch at startup and run in an infinite loop on the PI
- The settings will be loaded from the JSON file at launch and can be updated through the server, either by using the App or the Alexa. The JSON file will be updated with the new settings incase the device reboots or goes offline.
- Consits of 4 low priority threads
  - Automatic Watering: Runs even if the device is offline. Uses values stored in the settings
  - Automatic Measurements: Gets sensor readings and sends them to the server at regular intervals
  - MQTT Receiver: Listens for MQTT messages
  - MQTT Sender: Sends MQTT messages to the server when needed

#### Sensors
- ADC               (ADS1115)
- Moisture/Humidity (SI7021)
- Analog Moisture sensor

#### GPIO
- Water pump controlled through a NPN transistor

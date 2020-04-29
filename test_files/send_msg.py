import paho.mqtt.client as mqtt
import ssl
import smbus
import math


bus = smbus.SMBus(1)
raw_temp = bus.read_i2c_block_data(0x40,0xE3,2)
raw_humid = bus.read_i2c_block_data(0x40,0xE5,2)
Temperature = 175.72*(raw_temp[0]<<8 | raw_temp[1])/65536.0 - 46.85
Humidity    = 125*(raw_humid[0]<<8 | raw_humid[1])/65536.0 - 6.0

#print("Temp:", Temperature)
#print("Humid:", Humidity)


client = mqtt.Client()
client.tls_set(ca_certs="py_cert/mosquitto.org.crt",certfile="py_cert/client.crt",keyfile="py_cert/client.key",tls_version=ssl.PROTOCOL_TLSv1_2)
client.connect("test.mosquitto.org",port=8884)

client.publish("IC.embedded/obedient_fighting_snakes/sensor","T:"+str(round(Temperature,2))+";H:"+str(round(Humidity,2)))


#add threading to allow for sending and recieving at the same time

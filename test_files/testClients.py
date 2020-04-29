import paho.mqtt.client as mqtt
import ssl
from time import sleep
cert = ["py_cert/mosquitto.org.crt","py_cert/client.crt","py_cert/client.key"]
ourMQTT = "IC.embedded/obedient_fighting_snakes/"

def on_connect(client, userdata, flags, rc):
    if (rc == 0):
        print(userdata, "sucessfully connected to server")


client = mqtt.Client(userdata="client") #pass all the data needed inside callbacks. remember that those are pointers.
client.tls_set(ca_certs=cert[0], certfile=cert[1],keyfile=cert[2],tls_version=ssl.PROTOCOL_TLSv1_2)
client.on_connect = on_connect
client.connect("test.mosquitto.org",8884)
#sends to ourMQTT/measurementRead thread

client.publish(ourMQTT+"measurementRead", "hello")

# try:
#     client.loop_start()
#     wait(5)
#     client.publish(ourMQTT+"measurementRead", "hello")
#     while True:
#         pass
# except:
#     client.loop_stop()

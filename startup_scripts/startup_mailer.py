receiver_email = ["xxxxxxx@gmail.com","xxxxxxx@ic.ac.uk"]

import smtplib, ssl
import subprocess
import socket
import os
from datetime import datetime
import time
import platform

print("Running mailing script")

##CHECK INTERNET
def ping(host):
    param = '-n' if platform.system().lower()=='windows' else '-c'
    command = ['ping', param, '1', host]
    return subprocess.call(command) == 0
count = 0
while( not ping("google.com")):
    time.sleep(1)
    count += 1

print("Succesfull ping after", count, "Seconds")

##GET IP
arg="ip route list"
p=subprocess.Popen(arg,shell=True,stdout=subprocess.PIPE)
data = p.communicate()
split_data = data[0].split()
indx = -1
for i,c in enumerate(split_data):
    tmp= str(c)
    if("src" in tmp):
        indx = i+1
        break
if(indx == -1):
    exit(-1)
ip = str(split_data[indx])[2:-1]
prev_ip = "-1"
read_data = ""
with open("prev_ip.txt") as f:
    read_data = f.read() 
if(read_data == ip):
    print("IP the same as before", ip)
    exit(1)
else:
    with open("prev_ip.txt",'w') as f:
        f.write(ip)
    

##GET TIME AND DATE
    #c = ntplib.NTPClient()
    #response = c.request('europe.pool.ntp.org', version=3)
    #current_time = time.ctime(response.tx_time)
if(count > 2):
    time.sleep(10)
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
current_date = now.strftime("%Y/%m/%d")


##SEND EMAIL
print("Sending Emails")
port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "xxxxxxx@gmail.com"
password = *******


message = """\
Subject: Embedded IP: """ + ip + """



IP: """ + ip  + """
Turned on """ + current_date + """ """ + current_time + """."""


context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    for email in receiver_email:
        server.sendmail(sender_email, email, message)
        pass


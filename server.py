from pythonosc.udp_client import SimpleUDPClient
from socket import socket, SOCK_STREAM, AF_INET
import numpy as np
import time as t

addresses={"127.0.0.1":7000}
server_ip="127.0.0.1:7001"
oscclients = []
socketclients = []
for ip,port in addresses.items():
    oscclients.append(SimpleUDPClient(ip, port))

server = socket(AF_INET,SOCK_STREAM)
server.bind((server_ip.split(":")[0],int(server_ip.split(":")[1])))
server.listen(5)

def send_message(address,message):
    if type(message) == type(np.array([])):
        message = message.tolist()
    for client in oscclients:
        try:
            client.send_message(address, message)
        except OSError as e:
            print("ERROR: ",e)

def on_connection():
    socketclients.append(server.accept())
    print("connected")

def on_close():
    for client in socketclients:
        print(client[0])
        client[0].close()

def send_image(image):
    try:
        for client in socketclients:
            client[0].sendall((np.array("size: "+str(image.shape[0])+" "+str(image.shape[1])+" "+str(image.shape[2])+" ")).tobytes())
            client[0].sendall(image.reshape(image.shape[0]*image.shape[1]*image.shape[2]).tobytes())
    except:
        print("failted to send")

print("start")
on_connection()
while(True):
    send_message("/hi","hi")
    send_image(np.random.randint(0,255,(10,10,3),dtype=np.uint8))
    t.sleep(2)
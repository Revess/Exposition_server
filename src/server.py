from pythonosc.udp_client import SimpleUDPClient
import numpy as np
import time as t
from PIL import Image

class SERVER():
    def __init__(self,addresses={"127.0.0.1":7000}):
        self.oscclients = []
        self.addresses = []
        for ip,port in addresses.items():
            self.oscclients.append(SimpleUDPClient(ip, port))
            self.addresses.append([ip,port])

    def send_message(self,address,message):
        if type(message) == type(np.array([])):
            message = message.tolist()
        for client in self.oscclients:
            try:
                client.send_message(address, message)
            except :
                print("ERROR!")
    
    def get_clients(self):
        return self.addresses

    def set_client(self, ip, port):
        self.addresses.append([ip,port])
        self.oscclients.append(SimpleUDPClient(ip,port))
from pythonosc.udp_client import SimpleUDPClient
import numpy as np

class OSC_SERVER():
    def __init__(self,addresses={"127.0.0.1":7000}):
        self.clients = []
        for ip,port in addresses.items():
            self.clients.append(SimpleUDPClient(ip, port))

    def send_message(self,address,message):
        if type(message) == type(np.array([])):
            message = message.tolist()
        for client in self.clients:
            client.send_message(address, message)
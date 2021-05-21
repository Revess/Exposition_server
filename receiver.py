from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from PIL import Image
import time as t
import numpy as np

def print_handler(address, *args):
    if "img" not in address:
        print(f"{address}: {args}")
    elif "img" in address:
        print(f"{address}: {args}")

def default_handler(address, *args):
    if "img" not in address:
        print(f"DEFAULT {address}: {args}")
    elif "img" in address or "event" in address:
        print(f"DEFAULT{address}: {args}")

print("start osc_server")
dispatcher = Dispatcher()
dispatcher.map("/something/*", print_handler)
dispatcher.set_default_handler(default_handler)
ip = "127.0.0.1"
port = 7000
server = BlockingOSCUDPServer((ip, port), dispatcher)
server.serve_forever()  # Blocks forever
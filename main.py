# from src import global_time, osc_manager, processing_block, GUI
import os
import threading as td
import argparse

import src.global_manager as manager
from src.file_manager import make_folder, save_json, load_json
from src.global_time import GLOBAL_TIME
from src.osc_manager import OSC_SERVER
from src.processing_block import Processing_block

from src.GUI import GUI

parser = argparse.ArgumentParser(description='Interactive_art_server',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--gui_type', default="terminal", type=str, required=False, help='arguments may either be terminal or app')
parser.add_argument('--time_maximum', default=10, type=int, required=False, help='set maximum of the timer')
parser.add_argument('--addresses', default="127.0.0.1:7000 192.168.178.1:7000", type=str, required=False, help='set addresses as a ip and port in form of a dict')

#TODO: make global settings variable which is editable by the terminal interaction

class Main():
    def __init__(self,parser):
        args = parser.parse_args()
        ##Server_setup
        addresses = dict()
        for address in args.addresses.split():
            address = address.split(":")
            addresses.update({address[0]:int(address[1])})
        self.osc_server = OSC_SERVER(addresses)

        ##Globals
        self.global_manager = manager.global_manager()
        self.global_manager.set_settings(load_json("./data/settings/default.json"))

        ##create and check folder structure integraty
        self.user_dir = self.init_structure()
        
        self.clock = GLOBAL_TIME(args.time_maximum, self.osc_server, self.global_manager)
        self.processing_block = Processing_block(self.global_manager, self.osc_server)
        self.gui = GUI(self.user_dir, self.global_manager)

        #create threads
        self.clock_thread = td.Thread(target=self.clock.event_handler)
        self.processing_thread = td.Thread(target=self.processing_block.run_process)
        self.gui_thread = td.Thread(target=self.gui.run_gui)

    def init_structure(self):
        paths = [
            "./data/settings/user_settings",
            "./data/input_images",
            "./data/models",
            "./data/model_output/convolution_images",
            "./data/model_output/kernels",
            "./data/model_output/other",
            "./data/model_output/weights",
        ]
        for path in paths:
            make_folder(path)
        save_json(  {"event_times": {
                        "booting_time": 0,
                        "morph_1_time": 2,
                        "analysis_time": 3,
                        "morph_2_time": 7,
                        "context_time": 8
                        },
                    "event_order": ["booting","morph_1","analysis","morph_2","context"],
                    "GUI": "terminal"},"./data/settings/default.json")
        del paths
        return "./data/settings/user_settings/"

    def start(self):
        ##start the threads
        self.processing_thread.start()
        self.clock_thread.start()
        self.gui_thread.start()

    def run(self):
        ##run the code until broken
        self.clock.reset_clock()
        while(True):
            if self.global_manager.get_command() == 'exit':
                break
        self.kill()

    def kill(self):
        ##join the threads
        self.clock_thread.join()
        self.processing_thread.join()
        self.gui_thread.join()

if __name__ == "__main__":
    main = Main(parser)
    main.start()
    main.run()
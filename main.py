# from src import global_time, osc_manager, processing_block, GUI
import os
import threading as td
import argparse

import src.global_manager as manager
from src.file_manager import make_folder, save_json, load_json
from src.global_time import GLOBAL_TIME
from src.server import SERVER
from src.processing_block import Processing_block
from src.GUI import GUI

parser = argparse.ArgumentParser(description='Interactive_art_server',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--addresses', default="127.0.0.1:7000 192.168.137.184:7000 192.168.137.17:7000", type=str, required=False, help='set addresses as a ip and port in form of a dict')

#TODO: make global settings variable which is editable by the terminal interaction

class Main():
    def __init__(self,parser):
        args = parser.parse_args()
        ##Server_setup
        addresses = dict()
        for address in args.addresses.split():
            address = address.split(":")
            addresses.update({address[0]:int(address[1])})
        self.server = SERVER(addresses)

        ##Globals
        self.global_manager = manager.global_manager()

        ##create and check folder structure integrity
        self.user_dir = self.init_structure()
        self.global_manager.set_settings(load_json("./data/settings/default.json"))

        self.processing_block = Processing_block(self.global_manager, self.server)
        while not self.global_manager.get_loading_status():
            pass
        self.clock = GLOBAL_TIME(self.global_manager.get_settings()["phase_times"]["next_phase_time"]*60, self.server, self.global_manager)
        self.gui = GUI(self.user_dir, self.global_manager, self.clock, self.server)

        #create threads
        self.clock_thread = td.Thread(target=self.clock.event_handler)
        self.processing_booting_thread = td.Thread(target=self.processing_block.run_time_based_values)
        self.processing_analysis_thread = td.Thread(target=self.processing_block.run_image_rendering)
        self.gui_thread = td.Thread(target=self.gui.run_gui)

    def init_structure(self):
        paths = [
            "./data/settings/user_settings",
            "./data/input_images",
            "./data/models",
            "./data/model_output/images",
            "./data/model_output/kernels",
            "./data/model_output/other",
            "./data/model_output/weights",
        ]
        for path in paths:
            make_folder(path)
        save_json(  {"phase_times": {
                        "branding_time": 0,
                        "booting_time": 1,
                        "morph_1_time": 3,
                        "analysis_time": 4,
                        "morph_2_time": 6,
                        "context_time": 7,
                        "next_phase_time": 9
                        },
                    "generative_events": {
                        "booting_time": {
                            "trigger_1": [0,0.25],
                            "trigger_2": [0.5,0.25],
                            "trigger_3": [0.3,0.25]
                        },
                        "booting_time": {
                            "trigger_1": [0,0.25],
                            "trigger_2": [1,0.25],
                            "trigger_3": [2,0.25]
                        },
                        "analysis_time": {
                            "switch_img": 0.8
                        }
                    }
                    },"./data/settings/default.json")
        del paths
        return "./data/settings/user_settings/"

    def start(self):
        ##start the threads
        self.processing_booting_thread.start()
        self.processing_analysis_thread.start()
        self.clock_thread.start()
        self.gui_thread.start()

    def run(self):
        ##run the code until broken
        # self.clock.reset_clock()
        while(True):
            if self.global_manager.get_command() == 'exit':
                break
        self.kill()

    def kill(self):
        ##join the threads
        self.clock_thread.join()
        self.processing_booting_thread.join()
        self.processing_analysis_thread.join()
        self.gui_thread.join()

if __name__ == "__main__":
    main = Main(parser)
    main.start()
    main.run()
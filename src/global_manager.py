from random import randint as rnd
import os

class global_manager():
    def __init__(self):
        self.command = ''
        self.settings = {}
        self.event_header = -3
        self.event = []
        self.num_of_events = 0
        self.changes = True
        self.loading_AI = False
        self.maximum = 0
        self.analysis_ready = False
        self.progress_bars = {}
        self.generative_events = None
        self.directory = "./data/input_images/"
        self.loading_image = rnd(0,len(os.listdir(self.directory))-1)

    def get_changes(self):
        return self.changes

    def set_changes(self,state):
        self.changes = state

    def get_command(self):
        return self.command

    def set_command(self,command):
        self.command = command

    def get_settings(self):
        return self.settings

    def set_settings(self,settings):
        self.num_of_events = len(settings["phase_times"])-1
        self.settings = settings
        self.event = sorted(self.settings["phase_times"].items(), key=lambda item: item[1])[self.event_header][0]
        if self.event in self.settings["generative_events"].keys():
            self.generative_events = self.settings["generative_events"][self.event].items()
        self.changes = True
        self.maximum = sorted(self.settings["phase_times"].items(), key=lambda item: item[1])[-1][1]

    def get_maximum(self):
        return self.maximum*60

    def get_event(self):
        return self.event

    def get_event_time(self):
        return sorted(self.settings["phase_times"].items(), key=lambda item: item[1])[self.event_header][1]

    def get_next_event_time(self):
        self.num_of_events = len(self.settings["phase_times"])
        event_header = self.event_header
        if event_header < 0:
            event_header+=1
        else:
            event_header = (self.event_header+1) % self.num_of_events
        return sorted(self.settings["phase_times"].items(), key=lambda item: item[1])[event_header][1]

    def next_event(self):
        self.num_of_events = len(self.settings["phase_times"])
        if self.event_header < 0:
            self.event_header+=1
        else:
            self.event_header = (self.event_header+1) % self.num_of_events
        self.event = sorted(self.settings["phase_times"].items(), key=lambda item: item[1])[self.event_header][0]
        if self.event in self.settings["generative_events"].keys():
            self.generative_events = self.settings["generative_events"][self.event].items()
        else:
            self.generative_events = None

    def finished_loading(self):
        self.loading_AI = True

    def get_loading_status(self):
        return self.loading_AI

    def set_analysis_ready(self,process):
        self.analysis_ready = process

    def get_analysis_ready(self):
        return self.analysis_ready

    def get_progress_bars(self):
        return self.progress_bars

    def set_progress_bar(self,name,total):
        self.progress_bars.update({name:[total,0]})

    def update_progress_bar(self,name,index):
        self.progress_bars[name][1] = index

    def remove_progress_bar(self,name):
        if name in self.progress_bars.keys():
            del self.progress_bars[name]

    def get_generative_event(self):
        return self.generative_events

    def set_input_img(self):
        self.loading_image = rnd(0,len(os.listdir(self.directory))-1)

    def get_input_img(self):
        return self.loading_image
import time as t

class GLOBAL_TIME():
    def __init__(self,maximum,server,global_manager):
        self.server = server
        self.global_manager = global_manager
        self.start = t.time()
        self.maximum = maximum
        self.settings = self.global_manager.get_settings()
        self.event = self.settings["event_order"][self.global_manager.get_event_header()]
        # self.event_time = 
    
    def get_time(self):
        return t.time()-self.start

    def reset_clock(self):
        self.start = t.time()

    def get_maximum(self):
        return self.maximum

    def set_maximum(self,maximum):
        self.maximum

    def event_handler(self):
        while(True):
            self.settings = self.global_manager.get_settings()
            self.event = self.settings["event_order"][self.global_manager.get_event_header()]
            if self.global_manager.get_command() == 'exit':
                break
            if self.get_time() >= self.settings["event_times"][self.event+"_time"] and self.global_manager.get_finished_processes():
                self.global_manager.set_event_header(self.global_manager.get_event_header()+1)
                self.event = self.settings["event_order"][self.global_manager.get_event_header()]
                self.global_manager.set_finished_processes(False)
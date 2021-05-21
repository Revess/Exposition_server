import time as t
from random import randint as rnd
import os

class GLOBAL_TIME():
    def __init__(self,maximum,server,global_manager):
        self.server = server
        self.global_manager = global_manager
        self.start = t.time()
        self.maximum = maximum
        self.event_time = self.global_manager.get_next_event_time()*60
        self.start -= self.global_manager.get_event_time()*60
        self.stepts = 10
        self.increments = [((self.event_time-(self.global_manager.get_event_time()*60))*(i/10))+(self.global_manager.get_event_time()*60) for i in range(self.stepts)]
        self.increments_header = 0
        self.server.send_message("/event","start_"+str(self.global_manager.get_event()[:-5]))
        self.generative_events = None
        self.trigger_time = 0
        self.server.send_message("/img/input",[self.global_manager.get_input_img()+1])

    def get_time(self):
        return t.time()-self.start

    def reset_clock(self):
        self.start = t.time()

    def get_maximum(self):
        return self.maximum

    def set_maximum(self,maximum):
        self.maximum = maximum

    def event_handler(self):
        while(True):
            current_time = self.get_time()
            self.maximum = self.global_manager.get_maximum()
            global_change = rnd(0,100000)/100
            if self.global_manager.get_command() == 'exit':
                break
            if current_time >= self.event_time:
                self.server.send_message("/img/input",[self.global_manager.get_input_img()+1])
                self.global_manager.next_event()
                self.server.send_message("/event","start_"+str(self.global_manager.get_event()[:-5]))
                if str(self.global_manager.get_event()[:-5]) == "morph_2":
                    self.global_manager.set_analysis_ready(False)
                self.event_time = self.global_manager.get_next_event_time()*60
                self.increments = [((self.event_time-(self.global_manager.get_event_time()*60))*(i/10))+(self.global_manager.get_event_time()*60) for i in range(self.stepts)]
                self.increments_header=0
                if current_time >= self.get_maximum():
                    self.global_manager.set_input_img()
                    self.server.send_message("/img/input",[self.global_manager.get_input_img()+1])
                    self.trigger_time=0
                    self.reset_clock()
            elif self.increments_header < len(self.increments):
                if current_time >= self.increments[self.increments_header]:
                    self.server.send_message("/event",str(self.global_manager.get_event()[:-5])+"_"+str(self.increments_header+1))
                    self.increments_header+=1
            if self.global_manager.get_generative_event()!= None and current_time >= self.trigger_time:
                for key,value in self.global_manager.get_generative_event():
                    chance = rnd(1,100)
                    if key == "switch_img":
                        self.server.send_message("/img/input",[self.global_manager.get_input_img()+1])
                        if chance <= value*100:
                            directory = "./data/model_output/images/"
                            for folder in os.listdir(directory):
                                chance = rnd(1,100)
                                if ("conv" in folder or "mp" in folder) and chance <= value*100:
                                    self.server.send_message("/img/"+folder,[rnd(1,len(os.listdir(directory+folder)))])
                                elif ("dense" in folder or "flatten" in folder) and chance <= value*100:
                                    self.server.send_message("/img/"+folder,[rnd(1,len(os.listdir(directory+folder)))])
                    elif current_time >= (self.event_time/100)*value[0] and chance <= value[1]*100:
                        self.server.send_message("/event/subevent",str(self.global_manager.get_event()[:-5])+"_"+str(key))
                self.trigger_time=current_time+0.5
            if self.global_manager.get_event() == "branding":
                if global_change <= 0.01:
                    self.server.send_message("/system","ip_connected: "+str(rnd(0,255))+"."+str(rnd(0,255))+"."+str(rnd(0,255))+"."+str(rnd(0,255))+":"+str(rnd(5000,10000)))
                if global_change>0.01 and global_change <= 0.02:
                    self.server.send_message("/system","ip_disconnected: "+str(rnd(0,255))+"."+str(rnd(0,255))+"."+str(rnd(0,255))+"."+str(rnd(0,255))+":"+str(rnd(5000,10000)))
from src.file_manager import save_json, load_json, make_folder
import os
import curses
import time as t
import random
import threading as td
from math import floor

class GUI():
    def __init__(self, user_dir, global_manager, clock, server):
        self.user_dir = user_dir
        self.server = server
        self.global_manager = global_manager
        self.clock = clock
        self.history = []
        self.screen = curses.initscr()
        self.screen_size = self.screen.getmaxyx()
        self.user_input = ['']
        self.block = 0
        self.box_dimension = dict()
        self.frame_rate = 1/5
        self.boxes = dict(
            {
                "timer": self.screen.derwin(
                    floor(self.screen_size[0]*0.1), floor(self.screen_size[1]*0.5),
                    0,0
                ),
                "connections": self.screen.derwin(
                    floor(self.screen_size[0]*0.4), floor(self.screen_size[1]*0.5),
                    floor(self.screen_size[0]*0.6), 0
                ),
                "json_data": self.screen.derwin(
                    floor(self.screen_size[0]*0.9), floor(self.screen_size[1]*0.5),
                    floor(self.screen_size[0]*0.1), floor(self.screen_size[1]*0.5)
                ),
                "progress": self.screen.derwin(
                    floor(self.screen_size[0]*0.5), floor(self.screen_size[1]*0.5),
                    floor(self.screen_size[0]*0.1), 0
                ),
                "input": self.screen.derwin(
                    floor(self.screen_size[0]*0.1), floor(self.screen_size[1]*0.5),
                    0,floor(self.screen_size[1]*0.5)
                )
            })
        for key, value in self.boxes.items():
            self.box_dimension.update({key:value.getmaxyx()})
        self.screen.refresh()
        for key, value in self.boxes.items():
            value.box()
            value.refresh()

    def resize(self):
        resize = curses.is_term_resized(self.screen_size[0],self.screen_size[1])
        if resize is True:
            self.screen_size = self.screen.getmaxyx()
            self.screen.clear()
            curses.resize_term(self.screen_size[0],self.screen_size[1])
    
    def clear(self, exceptions="all"):
        if "screen" in exceptions or exceptions == 'all':
            self.screen.clear()
        for key, value in self.boxes.items():
            if key in exceptions or exceptions == 'all':
                value.box()
                value.clear()

    def refresh(self, exceptions="all"):
        if "screen" in exceptions or exceptions == 'all':
            self.screen.refresh()
        for key, value in self.boxes.items():
            if key in exceptions or exceptions == 'all':
                value.box()
                value.refresh()

    def run_input(self):
        while(True):            
            self.boxes["input"].clear()
            self.boxes["input"].box()
            curses.curs_set(1)

            for index in range(len(self.history)):
                self.boxes["input"].addstr(
                    self.box_dimension["input"][0]-(3+index),
                    1,
                    str(self.history[len(self.history)-1-index]))
                
            self.boxes["input"].addstr(self.box_dimension["input"][0]-2,1,">>> ")
            self.boxes["input"].refresh()

            self.user_input = self.boxes["input"].getstr(self.box_dimension["input"][0]-2,5,200).decode().lower().split()

            if len(self.user_input) == 0:
                ##add to history list
                self.history.append("Invalid Input")
                if len(self.history) >= self.box_dimension["input"][0]-2:
                    self.history.pop(0)
            else: 
                if self.user_input[0] == 'exit':
                    self.global_manager.set_command(self.user_input[0])
                    break
                elif self.user_input[0] == 'time' and len(self.user_input) >= 4:
                    settings = self.global_manager.get_settings()
                    current_time = 0
                    sorted_list = sorted(settings["event_times"].items(), key=lambda item: item[1])
                    if self.user_input[1] == 'set':
                        for index,key_value in enumerate(sorted_list):
                            key = key_value[0]
                            value = key_value[1]
                            settings["event_times"][key] = current_time
                            if self.user_input[2] == key[:-5]:
                                current_time += int(self.user_input[3])
                            elif key != "next_phase_time":
                                current_time += (sorted_list[index+1][1])-value
                        self.global_manager.set_settings(settings)
                    '''
                    elif self.user_input[1] == 'add' and len(self.user_input) >= 5:
                        self.user_input[2]+="_time"
                        sorted_list.insert(int(self.user_input[4]),(self.user_input[2],float(self.user_input[3])))
                        print(sorted_list)
                        settings["event_times"].update({self.user_input[2]:float(self.user_input[3])})
                        for index,key_value in enumerate(sorted_list):
                            key = key_value[0]
                            value = key_value[1]
                            settings["event_times"][key] = current_time
                            if key != "next_phase_time":
                                current_time += ((sorted_list[index+1][1])-value)
                        self.global_manager.set_settings(settings)
                    '''
                elif self.user_input[0] == "load_settings" and len(self.user_input) >= 2:
                    if self.user_input[1] == "default":
                        self.global_manager.set_settings(load_json("./data/settings/default.json"))
                    elif self.user_input[1] in os.listdir("./data/settings/user_settings"):
                        self.global_manager.set_settings(load_json("./data/settings/user_settings"+self.user_input[1]+".json"))
                    elif len(os.listdir("./data/settings/user_settings")) == 0:
                        self.history.append("No custom settings created yet")
                    else:
                        self.history.append("File not existing, the following files are available:")
                        for files__ in os.listdir("./data/settings/user_settings"):
                            self.history.append(os.path.splitext(files__)[0])
                elif self.user_input[0] == "save_settings":
                    if len(self.user_input) == 1:
                        save_json(self.global_manager.get_settings(),"./data/settings/user_settings/"+str(len(os.listdir("./data/settings/user_settings/"))+1)+".json")
                    elif len(self.user_input) >= 2:
                        save_json(self.global_manager.get_settings(),"./data/settings/user_settings/"+self.user_input[2]+".json")
                elif self.user_input[0] == "connection" and len(self.user_input) >= 3:
                    if self.user_input[1] == "add":
                        self.server.set_client(self.user_input[2].split(":")[0],int(self.user_input[2].split(":")[1]))

                ##add to history list
                self.history.append(' '.join(self.user_input))
                if len(self.history) >= self.box_dimension["input"][0]-2:
                    self.history.pop(0)
                
            t.sleep(self.frame_rate)

    def run_json_box(self):
        offset = 6
        while(True):
            if self.global_manager.get_changes():
                local_settings = self.global_manager.get_settings()
                self.boxes["json_data"].clear()
                self.boxes["json_data"].box()
                curses.curs_set(0)

                self.boxes["json_data"].addstr(1, round(self.box_dimension["json_data"][1]/2)-round(len("CURRENT_SETINGS")/2),"CURRENT_SETINGS")
                self.boxes["json_data"].refresh()

                index = 0
                for key, value in local_settings.items():
                    if type(value) == type(str()):
                        self.boxes["json_data"].addstr(index+3, offset, (str(key)+": "))
                        self.boxes["json_data"].addstr(index+3, len((str(key)+": "))+offset, str(value))
                        index+=1
                    
                    elif type(value) == type(dict()):
                        self.boxes["json_data"].addstr(index+3, offset, (str(key)+": {"))
                        index+=1
                        if key == "generative_events":
                            for sub_key, sub_value in value.items():
                                if type(sub_value) == type(dict()):
                                    self.boxes["json_data"].addstr(index+3, offset+4, (str(sub_key)+": {"))
                                    index+=1
                                    for sub_sub_key, sub_sub_value in sorted(sub_value.items(), key=lambda item: item[1]):
                                        if type(sub_sub_value) == type(list()):
                                            self.boxes["json_data"].addstr(index+3, offset+8, (str(sub_sub_key)+": ["))
                                            index+=1
                                            for output in sub_sub_value:
                                                self.boxes["json_data"].addstr(index+3, offset+12, (str(output)+","))
                                                index+=1
                                            self.boxes["json_data"].addstr(index+3, offset+8, "]")
                                            index+=1
                                        elif type(sub_sub_value) == type(float()) or type(sub_sub_value) == type(int()):
                                            self.boxes["json_data"].addstr(index+3, offset+8, (str(sub_sub_key)+": "+str(sub_sub_value)))
                                            index+=1
                                            
                                    '''
                                        self.boxes["json_data"].addstr(index+3, offset+5, (str(sub_sub_dict_key)+": ["))
                                        self.boxes["json_data"].addstr(index+3, len((str(sub_sub_dict_key)+": ["))+offset+5, (str(sub_sub_dict_value[0])+", "))
                                        self.boxes["json_data"].addstr(index+3, len((str(sub_sub_dict_key)+": ["))+len(str(sub_sub_dict_value[0])+", ")+offset+5, (str(sub_sub_dict_value[1])+"]"))
                                        index+=1
                                    '''
                                    self.boxes["json_data"].addstr(index+3, offset+4, "}")
                                    index+=1
                                else:
                                    print(key,sub_key,sub_value)
                        elif key == "phase_times":
                            for sub_key, sub_value in sorted(value.items(), key=lambda item: item[1]):
                                self.boxes["json_data"].addstr(index+3, offset+4, (str(sub_key)+": "))
                                self.boxes["json_data"].addstr(index+3, len((str(sub_key)+": "))+offset+4, (str(sub_value)+","))
                                index+=1
                        self.boxes["json_data"].addstr(index+3, offset, "}")
                        index+=2

                    if type(value) == type(list()):
                        self.boxes["json_data"].addstr(index+3, offset, (str(key)+": ["))
                        index+=1
                        for sub_dict_value in value:
                            self.boxes["json_data"].addstr(index+3, offset+4, str(sub_dict_value))
                            index+=1
                        index+=1
                        self.boxes["json_data"].addstr(index+3, offset, "]")
                        index+=2

                self.boxes["json_data"].refresh()

            if len(self.user_input) != 0:
                if self.user_input[0] == 'exit':
                    break
            self.global_manager.set_changes(False)
            t.sleep(1)

    def run_timer(self):
        while(True):
            self.boxes["timer"].clear()
            self.boxes["timer"].box()
            curses.curs_set(0)

            self.boxes["timer"].addstr(1, round(self.box_dimension["timer"][1]/2)-round(len("CURRENT_CLOCK")/2),"CURRENT_CLOCK")
            current_time_s = round(self.clock.get_time(),2)
            current_time_s = "Current_time: M: "+str(int(current_time_s/60))+" S: "+str(int(current_time_s%60))
            event = "Current event: "+str(self.global_manager.get_event())[:-5]
            # self.server.send_message("/system",current_time_s)
            self.boxes["timer"].addstr(3, round(self.box_dimension["timer"][1]/2)-round(len(current_time_s)/2), current_time_s)
            self.boxes["timer"].addstr(4, round(self.box_dimension["timer"][1]/2)-round(len(event)/2),event)
            self.boxes["timer"].refresh()

            if len(self.user_input) != 0:
                if self.user_input[0] == 'exit':
                    break
            t.sleep(0.1)

    def run_progress_bars(self):
        while(True):
            self.boxes["progress"].clear()
            self.boxes["progress"].box()
            curses.curs_set(0)

            self.boxes["progress"].addstr(1, round(self.box_dimension["progress"][1]/2)-round(len("LOADING_PROGRESS")/2),"LOADING_PROGRESS")
            local_dict = self.global_manager.get_progress_bars().items()
            for index,name_bar in enumerate(local_dict):
                name = name_bar[0]
                bar = name_bar[1]
                percent = ("{0:." + str(1) + "f}").format(100 * (bar[1] / float(bar[0])))
                filledLength = int(30 * bar[1] // bar[0])
                char_type = '█' * filledLength + '-' * (30 - filledLength)
                output_string = f'\r{name} |{char_type}| {percent}% {bar[1]}/{bar[0]}'
                self.server.send_message("/system",output_string)
                self.boxes["progress"].addstr(3+index,round(self.box_dimension["progress"][1]/2)-round(len(output_string)/2),output_string)
            self.boxes["progress"].refresh()
            
            if len(self.user_input) != 0:
                if self.user_input[0] == 'exit':
                    break
            t.sleep(0.1)

    def run_connections(self):
        while(True):
            self.boxes["connections"].clear()
            self.boxes["connections"].box()
            curses.curs_set(0)
            clients = self.server.get_clients()
            self.boxes["connections"].addstr(1, round(self.box_dimension["connections"][1]/2)-round(len("LOCAL_CONNECTIONS")/2),"LOCAL_CONNECTIONS")
            for index,client in enumerate(clients):
                client = client[0]+":"+str(client[1])
                self.boxes["connections"].addstr(3+index, round(self.box_dimension["connections"][1]/2)-round(len(client)/2),client)
            self.boxes["connections"].refresh()

            if len(self.user_input) != 0:
                if self.user_input[0] == 'exit':
                    break
            t.sleep(0.1)

    def run_gui(self):
        threads = {
            "timer_thread": td.Thread(target=self.run_timer),
            "connections_thread": td.Thread(target=self.run_connections),
            "json_thread": td.Thread(target=self.run_json_box),
            "progress_thread": td.Thread(target=self.run_progress_bars),
            "input_thread": td.Thread(target=self.run_input)
        }
        for name, thread in threads.items():
            thread.start()
        for name, thread in threads.items():
            thread.join()

        while(True):
            self.screen.refresh()
            if self.user_input[0] == "exit":
                curses.curs_set(1)
                curses.endwin()
                return
from src.file_manager import save_json, load_json, make_folder
import os
import curses
import time as t
import random
import threading as td

class GUI():
    def __init__(self, user_dir, global_manager):
        self.user_dir = user_dir
        self.global_manager = global_manager
        self.history = []
        self.screen = curses.initscr()
        self.screen_size = self.screen.getmaxyx()
        self.user_input = ['']
        self.block = 0
        self.box_dimension = dict()
        self.frame_rate = 1/5
        self.boxes = dict(
            {
                "timer":curses.newwin(
                    round(self.screen_size[0]*0.7), round(self.screen_size[1]*0.5),
                    0, 0
                ),
                "json_data": curses.newwin(
                    round(self.screen_size[0]*0.7), round(self.screen_size[1]*0.5),
                    0, round(self.screen_size[1]*0.5)
                ),
                "input": curses.newwin(
                    round(self.screen_size[0]*0.3), self.screen_size[1],
                    self.screen_size[0]-round(self.screen_size[0]*0.3),0
                )    
            })
        for key, value in self.boxes.items():
            self.box_dimension.update({key:value.getmaxyx()})
        self.screen.refresh()
        for key, value in self.boxes.items():
            value.box()
            value.refresh()

        curses.endwin()

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
            self.boxes["input"].refresh()
                
            self.boxes["input"].addstr(self.box_dimension["input"][0]-2,1,">>> ")
            self.boxes["input"].refresh()

            self.user_input = self.boxes["input"].getstr(self.box_dimension["input"][0]-2,5,10).decode().lower().split()
            self.global_manager.set_command(self.user_input[0])

            if len(self.user_input) == 0:
                self.user_input = ['']
            if self.user_input[0] == 'exit':
                break
            self.history.append(' '.join(self.user_input))
            if len(self.history) >= self.box_dimension["input"][0]-2:
                self.history.pop(0)
            t.sleep(self.frame_rate)

    #TODO: FIX settings and global time
    def run_json_box(self):
        while(True):
            self.boxes["json_data"].clear()
            self.boxes["json_data"].box()
            curses.curs_set(0)

            self.boxes["json_data"].addstr(1, round(self.box_dimension["json_data"][1]/2),"CURRENT_SETINGS")
            self.boxes["json_data"].refresh()

            index = 0
            for key, value in self.global_manager.get_settings().items():
                self.boxes["json_data"].addstr(index+3, 1, (str(key)+": "))
                if type(value) == type(str()):
                    self.boxes["json_data"].addstr(index+3, len((str(key)+": "))+1, str(value))
                    index+=1
                
                elif type(value) == type(dict()):
                    index+=1
                    for sub_dict_key, sub_dict_value in sorted(value.items(), key=lambda item: item[1]):
                        self.boxes["json_data"].addstr(index+3, 4, (str(sub_dict_key)+": "))
                        self.boxes["json_data"].addstr(index+3, len((str(sub_dict_key)+": "))+4, (str(sub_dict_value)+","))
                        index+=1

                # elif type(value) == type(list):
                #     for sub_dict_value in value:
                #         self.boxes["json_data"].addstr(index+4, 1, str(sub_dict_value))

            self.boxes["json_data"].refresh()

            if self.user_input[0] == 'exit':
                break
            t.sleep(5)

    def run_timer(self):
        while(True):
            self.boxes["timer"].clear()
            self.boxes["timer"].box()
            curses.curs_set(0)

            self.boxes["timer"].addstr(1, round(self.box_dimension["timer"][1]/2),"CURRENT_CLOCK")
            self.boxes["timer"].refresh()

            if self.user_input[0] == 'exit':
                break
            t.sleep(5)

    def run_gui(self):
        threads = {
            "input_thread": td.Thread(target=self.run_input),
            "json_thread": td.Thread(target=self.run_json_box),
            "timer_thread": td.Thread(target=self.run_timer)
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
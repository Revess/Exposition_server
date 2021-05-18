from src.file_manager import save_json, load_json, make_folder
import os

class GUI():
    def __init__(self, GUI_type,user_dir, global_manager):
        self.user_dir = user_dir
        self.global_manager = global_manager
        self.GUI_type = GUI_type
        if self.GUI_type == 'terminal' :
            while(True):
                state = input("Would you like to load the default settings? (Y|N) ").lower().split()
                if state[0] == 'y':
                    self.settings = load_json("./data/settings/default.json")
                    break
                elif state[0] == 'n':
                    if len(os.listdir(self.user_dir)) != 0:
                        print("The following files are available:")
                        for files in os.listdir(self.user_dir):
                            print("-",os.path.splitext(files)[0])
                        while(True):
                            state = input("Which file should be loaded?")
                            if os.path.exists(self.user_dir+state[0]+".json"):
                                if ".json" in state[1]:
                                    state[1] = os.path.splitext(state[1])[0]
                                self.settings = load_json(self.user_dir+state[0]+".json")
                                break
                            else:
                                print("file does not exist")
                    else:
                        print("no user file available, falling back on the default")
                        self.settings = load_json("./data/settings/default.json")
                        break
                else:
                    print("not a valid input, please reply y or n")
        self.global_manager.set_settings(self.settings)

    def run_gui(self):
        if self.GUI_type.lower() == "terminal":
            self.terminal()
        elif self.GUI_type.lower() == "app":
            self.app()

    def app(self):
        pass

    def terminal(self):
        while(True):
            state = input(">>> ").lower().split()
            if len(state) > 0:
                if state[0] == "time":
                    if len(state) == 4:
                        if state[1] == "set":
                            if state[2] == "booting":
                                self.settings["phase_times"]["booting_time"] = int(state[3])
                            elif state[2] == "morph_1":
                                self.settings["phase_times"]["morph_1_time"] = int(state[3])
                            elif state[2] == "analysis":
                                self.settings["phase_times"]["analysis_time"] = int(state[3])
                            elif state[2] == "morph_2":
                                self.settings["phase_times"]["morph_2_time"] = int(state[3])
                            elif state[2] == "context":
                                self.settings["phase_times"]["context_time"] = int(state[3])
                            else:
                                print("setting does not exist")
                            self.global_manager.set_settings(self.settings)
                        elif state[1] == "add":
                            self.settings.update({state[2]:int(state[3])})
                            self.global_manager.set_settings(self.settings)
                        else:
                            print("You can either set or add a time setting")
                    else:
                        print("Not enough arguments given \n time [add|set] [event_name] [event_time]")

                elif state[0] == "save_settings":
                    if len(state) == 1:
                        print("No file name given")
                    else:
                        if ".json" in state[1]:
                            state[1] = os.path.splitext(state[1])[0]
                        save_json(self.settings,self.user_dir+state[1]+".json")

                elif state[0] == "load_settings":
                    if len(state) == 1:
                        print("No file name given")
                        if len(os.listdir(self.user_dir)) != 0:
                            print("The following files are available:")
                            for files in os.listdir(self.user_dir):
                                print("-",os.path.splitext(files)[0])
                    else:
                        if os.path.exists(self.user_dir+state[1]):
                            if ".json" in state[1]:
                                state[1] = os.path.splitext(state[1])[0]
                            self.settings = load_json(self.user_dir+state[1]+".json")
                            self.global_manager.set_settings(self.settings)
                        else:
                            print("File does not exist")
                
                elif state[0] == "load_default":
                    self.settings = load_json("./data/settings/default.json")
                    self.global_manager.set_settings(self.settings)
                
                
                elif state[0] == "get_info":
                    if start_booting:
                        current_phase = "booting"
                    if start_morph_1:
                        current_phase = "morphing"
                    if start_analysis:
                        current_phase = "analysis"
                    if start_morph_2:
                        current_phase = "second morph"
                    if start_context:
                        current_phase = "context"
                    print("Current phase: ", current_phase)
                    print("Current clock tick: ", event_timer.get_time())
                    print("Current settings ", settings)
                

                elif state[0] == "exit":
                    self.global_manager.set_command('exit')
                    return 0
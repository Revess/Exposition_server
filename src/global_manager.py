class global_manager():
    def __init__(self):
        self.command = ''
        self.settings = {}
        self.event_header = -1
        self.num_of_events = 0
        self.finished_processes = False

    def get_command(self):
        return self.command

    def set_command(self,command):
        self.command = command

    def get_settings(self):
        return self.settings

    def set_settings(self,settings):
        self.num_of_events = len(settings["event_order"])-1
        self.settings = settings

    def get_event_header(self):
        return self.event_header

    def set_event_header(self,value):
        self.num_of_events = len(self.settings["event_order"])-1
        self.event_header = value % self.num_of_events

    def get_finished_processes(self):
        return self.finished_processes

    def set_finished_processes(self,value):
        self.finished_processes = value
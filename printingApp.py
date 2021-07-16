##let's put all the main stuff here in the class
import GUI_code
import api_calls
from prepare_params import *
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from utils import *
import glob
import os.path
from pathlib import Path#monitor directory presence

class PrintApp():

    def __init__(self, loc):
        self.loc = loc

    
    def run(self):
        
        print("Tracked directory: " + self.loc)
        print("Starting tracking ...")

        # I have removed the global variable lines
        # Like we discussed I moved the whole control of the gui and api calls to the event handler
        self.start_watching()
        print("Observing done!")


    #this function could also be here
    def start_watching(self):
        observer = Observer()
        event_handler = MyHandler(observer, self.loc)#let's also pass the path, so we can monitor the directory 
        #(alternatively, modify the string returned by event.src_path)
        
        #it is not ideal to have the path hardcoded here
        #this could be something you would like to let users change without changint the code
        #we can make it a parameter to the main function or a global constant imported from a config file
        observer.schedule(event_handler, path=self.loc, recursive=False)
        observer.start()
        observer.join()#we can join here bc the thread terminates. (do we need the join here?)



#Trigger an event on file creation
class MyHandler(FileSystemEventHandler):

    gui = GUI_code.GUI()
    def __init__(self, observer, path):
        self.observer = observer
        self.path = path
        
        
    def on_created(self, event):
        #We do not want to unzip after arbitrarily predetrmined time.
        #Check if the event.src_path direcotry still exists and while exists do not do anything
        print("Here's src path", event.src_path)
        dir_path = Path(event.src_path)
        while True:
            if not dir_path.exists():#the directory does not exist
                break
        folder_path = self.path
        file_type = '\*zip'#look for the last .zip file
        files = glob.glob(folder_path + file_type)
        max_file = max(files, key=os.path.getctime)
        print ("Here is the last file", max_file) 
        lines = unzip_read(max_file)
        params_converted = get_final_params(lines)

        #Now, we need to start the GUI code
        func_name, record_trial_info, print_result = self.gui.start_GUI()

        #update the print_result obtained from GUI
        params_converted['print_eval'] = print_result
        #Populate DB
        self.populate_database(func_name, record_trial_info, params_converted)


    def populate_database(self, func_name, record_trial_info, params_converted):
        api = api_calls.API_calls()
        if func_name == "add_record":
            api.add_record(record_trial_info, params_converted)
        if func_name == "add_trial":
            api.add_trial(record_trial_info, params_converted)

    def stop(self):
        self.observer.stop()

        
        
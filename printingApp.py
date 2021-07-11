##let's put all the main stuff here in the class
import GUI_code
import populate_db
from prepare_params import *
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from utils import *

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
        event_handler = MyHandler(observer)
        #it is not ideal to have the path hardcoded here
        #this could be something you would like to let users change without changint the code
        #we can make it a parameter to the main function or a global constant imported from a config file
        observer.schedule(event_handler, path=self.loc, recursive=False)
        observer.start()
        observer.join()#we can join here bc the thread terminates.



#Trigger an event on file creation
class MyHandler(FileSystemEventHandler):

    def __init__(self, observer):
        # self.lines = lines  - try to go without this
        self.observer = observer
        
        
    def on_created(self, event):
        # self.stop() - keep observing

        #give permissions
        #os.chmod(event.src_path, stat.S_IRUSR|stat.S_IRGRP|stat.S_IROTH)
        init_size = -1
        print("Here's the source path returned by watchdog", event.src_path)
        
        #this while loop is also not ideal, but we can keep it for now
        while True:
            current_size = os.path.getsize(event.src_path)
            
            if current_size == init_size:
                break
            else:
                init_size = os.path.getsize(event.src_path)
                time.sleep(2)
        print("file copy has now finished")
        lines = unzip_read(event.src_path)
        params_converted = get_final_params(lines)

        #Now, we need to start the GUI code
        func_name, record_trial_info = GUI_code.start_GUI()

        #Populate DB
        self.populate_database(func_name, record_trial_info, params_converted)


    def populate_database(self, func_name, record_trial_info, params_converted):
        if func_name == "add_record":
            populate_db.add_record(record_trial_info, params_converted)
        if func_name == "add_trial":
            populate_db.add_trial(record_trial_info, params_converted)

    def stop(self):
        self.observer.stop()

        
        
##let's put all the main stuff here in the class
from os import utime
import GUI_code
import api_calls
from prepare_params import *
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from utils import *
import glob
import os.path
from pathlib import Path#monitor directory presence
import time

class PrintApp:
    """
    Driver class.
    """

    def __init__(self, loc, name_token):
        """
        Initialise PrintingApp class.

        Parameters
        ----------
        loc : str
            Path to the folder to monitor for creation of new .zip files.
        name_token : str
            Name associated with a REDCap API token to be used.

        Returns
        -------
        None.
        """

        self.loc = loc
        self.name_token = name_token

    
    def run(self):
        """
        Method called when the program starts running.
        
        Parameters
        ----------
        None.
        
        Returns
        -------
        None.
        """
        
        print("Tracked directory: " + self.loc)
        print("Here is the name associated with a token: " + self.name_token)
        #add token as class attribute to API_calls
        api_calls.API_calls.token = get_token(self.name_token)
        print("Starting tracking ...")

        # I have removed the global variable lines
        # Like we discussed I moved the whole control of the gui and api calls to the event handler
        self.start_watching()
        print("Observing done!")


    #this function could also be here
    def start_watching(self):
        """
        Method where we start watching the required directory.  

        Parameters
        ----------
        None.

        Returns
        -------
        None.
        """

        observer = Observer()
        event_handler = MyHandler(observer, self.loc)
        
        observer.schedule(event_handler, path=self.loc, recursive=False)
        observer.start()
        observer.join()#we can join here bc the thread terminates. (do we need the join here?)



#Trigger an event on file creation
class MyHandler(FileSystemEventHandler):
    """
    Class with routines for monitoring file creation.    
    """
    gui = GUI_code.GUI()
    def __init__(self, observer, path):
        """
        Initialise MyHandler class.

        Parameters
        ----------
        observer : Observer object
            Instance of the Observer class used to observe the path.
        path : str
            Path to the folder to monitor for creation of new .zip files.
        
        Returns
        -------
        None.
        """
        self.observer = observer
        self.path = path
        
    def on_created(self, event):
        """
        Method triggered in the event of file/directory creation creation. Reads from the 
        latest created .zip file.

        Parameters
        ----------
        event : object
            Object containing source path that triggered the event.
        
        Returns
        -------
        None.
        """
        print("Here's src path", event.src_path)
        if not event.src_path.endswith(".zip"):
            print("Not .zip")
            return None
        folder_path = self.path
        file_type = '\*zip'#look for the last .zip file
        files = glob.glob(folder_path + file_type)
        max_file = max(files, key=os.path.getctime)
        print ("Here is the last file", max_file) 
        time.sleep(2)
        lines = unzip_read(max_file)
        params_converted = get_final_params(lines)

        #Now, we need to start the GUI code
        func_name, record_trial_info, print_result, folderPath = MyHandler.gui.start_GUI()

        #update the print_result obtained from GUI
        params_converted['print_eval'] = print_result
        #Populate DB
        self.populate_database(func_name, record_trial_info, params_converted, folderPath)

    def populate_database(self, func_name, record_trial_info, params_converted, folderPath):
        """
        Function that intiates the REDCap database population.

        Parameters
        ----------
        func_name : str
            One of the two function names corresponding to a new experiment or 
            a new trial of an old experiment.
        record_trial_info : dict
            Material information + printer information dictonary.
        params_converted : dcit
            Parameter information dictonary.

        Returns
        -------
        None.
        """
        api = api_calls.API_calls()
        if func_name == "add_record":
            api.add_record(record_trial_info, params_converted, folderPath)
        if func_name == "add_trial":
            api.add_trial(record_trial_info, params_converted, folderPath)

    def stop(self):
        """
        Method used to stop the worker thread(in case we ever need to).

        Parameters
        ----------
        None.

        Returns
        -------
        None.
        """
        self.observer.stop()
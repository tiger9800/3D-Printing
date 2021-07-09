from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from zipfile import ZipFile
import time
import os
import stat

#Trigger an event on file creation
class MyHandler(FileSystemEventHandler):

    def __init__(self, lines, observer):
        self.lines = lines 
        self.observer = observer
        
        
    def on_created(self, event):
        self.stop()#do not observe anymore
        #give permissions
        #os.chmod(event.src_path, stat.S_IRUSR|stat.S_IRGRP|stat.S_IROTH)
        init_size = -1
        print("Here's the source path returned by watchdof", event.src_path)
        while True:
            current_size = os.path.getsize(event.src_path)
            
            if current_size == init_size:
                break
            else:
                init_size = os.path.getsize(event.src_path)
                time.sleep(2)
        print("file copy has now finished")
        unzip_read(self.lines, event.src_path)
        
    def stop(self):
        self.observer.stop()
        

def start_watching(lines):
    observer = Observer()
    event_handler = MyHandler(lines, observer)
    observer.schedule(event_handler, path='C:\\Program Files\\Notepad++', recursive=False)
    observer.start()
    observer.join()#we can join here bc the thread terminates.


def unzip_read(lines, src_path):
    """
    Unzip the file and read its lines into lines. 
    
    src_path - path to the zip file.
    lines - list, passed by reference. 
    
    """
    #The function works by itself.
    with ZipFile(src_path, 'r') as zipObject: #Here, we need to unzip the file that was just created
        listOfFileNames = zipObject.namelist()
        for fileName in listOfFileNames:
            if fileName.endswith('.bpm'):
                # Extract a single file from zip
                with zipObject.open(fileName, 'r') as fd:
                    read_export(fd, lines)
                break

def read_export(file_descriptor, lines):
    """
    Parse the export file and modify the lines list(passed by reference).
    """
    line  = file_descriptor.readline().decode('ascii')#we need to decode because we get binary
    while line != "":
        lines.append(line)
        line = file_descriptor.readline().decode('ascii')
    del lines[:3]#do not add any meaning
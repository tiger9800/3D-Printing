from watchdog.events import FileSystemEventHandler
import time

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
        while True:
            current_size = os.path.getsize(event.src_path)
            
            if current_size == init_size:
                break
            else:
                init_size = os.path.getsize(event.src_path)
                time.sleep(2)
        print("file copy has now finished")
        fd = unzip_read(event.src_path)
        lines = read_export(fd)
        params = prepare_params.parse_export(lines)
        redcap_params = prepare_params.XML_to_REDCap(params)
        params_converted = prepare_params.params_clean_convert(redcap_params)
        #Now, we need to start the GUI code
        func_name, record_trial_info = GUI_code.start_GUI()
        if func_name == "add_record":
            populate_db.add_record(record_trial_info, params_converted)
        if func_name == "add_trial":
            populate_db.add_trial(record_trial_info, params_converted)
        
    def stop(self):
        self.observer.stop()
        



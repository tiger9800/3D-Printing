

from printingApp import PrintApp
#nice library for parsing cmd line arguments
import argparse
#utils for helper functions
from utils import *

## the code that you want to be executed first can be in the main function
## then you can rename this file to something nicer like "3D_printing_database" or something

def main(location):
    # in general I am a fan of object oriented design
    # it makes the code more modular
    # so let's put all the major things in one class

    #we can make the location a parameter for users to specify
    app = PrintApp(location)
    app.run()



"""
this gets executed when you run the python file from CMD
good practice is to parse any CMD arguments here 
and run the main function from here
"""

if __name__ == "__main__" :

    #nice way to parse arguments
    parser = argparse.ArgumentParser(description = 'This is the 3DP app, hellp')
    parser.add_argument('--loc',
                         type=dir_path, default=".", 
                         help='location that will be tracked for new files - default current forlder')
    args = parser.parse_args()

    main(args.loc)


    #this used to be here - moved it to app.run
    '''
    lines = []
    read_on_create.start_watching(lines)
    params = prepare_params.parse_export(lines)
    redcap_params = prepare_params.XML_to_REDCap(params)
    params_converted = prepare_params.params_clean_convert(redcap_params)
    #Now, we need to start the GUI code
    func_name, record_trial_info = GUI_code.start_GUI()
    if func_name == "add_record":
        populate_db.add_record(record_trial_info, params_converted)
    if func_name == "add_trial":
        populate_db.add_trial(record_trial_info, params_converted)
    '''

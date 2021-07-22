

from printingApp import PrintApp
#nice library for parsing cmd line arguments
import argparse
#utils for helper functions
from utils import *

## the code that you want to be executed first can be in the main function
## then you can rename this file to something nicer like "3D_printing_database" or something

<<<<<<< HEAD
def main(location, name_token):
=======
def main(location, token):
>>>>>>> 94041a393c62ccb73a9603f0c608efb0c15841b4
    # in general I am a fan of object oriented design
    # it makes the code more modular
    # so let's put all the major things in one class

    #we can make the location a parameter for users to specify
    app = PrintApp(location, name_token)
    app.run()



"""
this gets executed when you run the python file from CMD
good practice is to parse any CMD arguments here 
and run the main function from here
"""

if __name__ == "__main__" :

    #nice way to parse arguments
    parser = argparse.ArgumentParser(description = 'This is the 3DP app, hellp')
    #loc is an optional argument
    parser.add_argument('--loc',
                         type=dir_path, default=".", 
                         help='location that will be tracked for new files - default current forlder')
    parser.add_argument('name', 
                         help='name of a user for the token')
    args = parser.parse_args()

    main(args.loc, args.name)#name of the attributes


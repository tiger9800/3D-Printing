# utils.py is a good place to keep a bunch of helper functions

import os
from zipfile import ZipFile

def dir_path(string):
    '''
    check if path input parameter is valid
    '''
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


def read_export(file_descriptor):
    """
    Parse the export file and modify the lines list(passed by reference).
    """
    lines = []
    line  = file_descriptor.readline().decode('ascii')#we need to decode because we get binary
    while line != "":
        lines.append(line)
        line = file_descriptor.readline().decode('ascii')
    del lines[:3]#do not add any meaning
    return lines


def unzip_read(src_path):
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
                    return read_export(fd)
                break
    return None
    


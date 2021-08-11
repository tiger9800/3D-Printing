# utils.py is a good place to keep a bunch of helper functions
import api_calls
import os
from zipfile import ZipFile
import re
import datetime
import json
import os

def dir_path(string):
    '''
    Function checks if the path (string) is valid.

    Parameters
    ----------
    string : str
        String correpsonding to the path.

    Returns
    -------
    None.
    '''
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


def read_export(file_descriptor):
    """
    Function parses the XML-formatted export file list(passed by reference).

    Parameters
    ----------
    file_descriptor : file object
        file descriptor of an open XML-formatted file.

    Returns
    -------
    lines : list
        List of strings where each element corresponds to a line from the export file.
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
    Function unzips the file and read its lines into lines. 
    
    Parameters
    ----------
    src_path : str
        String path to the zip file.
    
    Returns
    -------
    lines : list
        List of strings where each element corresponds to a line from the export file.
    """
    #The function works by itself.
    with ZipFile(src_path, 'r') as zipObject: #Here, we need to unzip the file that was just created
        listOfFileNames = zipObject.namelist()
        for fileName in listOfFileNames:
            if fileName.endswith('.bpm'):
                # Extract a single file from zip
                with zipObject.open(fileName, 'r') as fd:
                    return read_export(fd)
    return None
    
def check_bran_logic(record_dict):
    """
    Function that delete the fields that are not supposed to be included in the record_dict because their branching logic
    is not satisfied. (Modfies record_dict by reference)

    Parameters
    ----------
    record_dict : dict
        Dictonary with field_name's as keys and field_values as values.

    Returns
    -------
    None.
    """
    api = api_calls.API_calls()
    branch_dict = api.get_branching_dep_to_indep()
    to_delete = []
    
    # print("Here dependnent to independent dict:", branch_dict)
    for dependent_field in record_dict:
        to_delete_flag = False
        if(dependent_field in branch_dict):
            for independent_field in branch_dict[dependent_field]:
                #if the value that the indep fields takes satisfies the branching logic for the dependent, then do not delete
                if(record_dict[independent_field] in branch_dict[dependent_field][independent_field]):
                    #do not delete
                    to_delete_flag = False
                    break#so to_delete = False is set last
                else:
                    to_delete_flag = True
        if(to_delete_flag):
            to_delete.append(dependent_field)
    
    #Delete the selected keys
    for key in to_delete:
        del record_dict[key]

def convert_to_numeric(record_dict):
    """
    Function converts string choices in to numeric choices according to the REDCAP project specifications.

    Parameters
    ----------
    record_dict : dict
        Dictonary with field_name's as keys and field_values as values.(modified by reference)
    
    Returns
    -------
    None.
    """
    api = api_calls.API_calls()
    metadata = api.get_metadata()
    name_choice_type = {field['field_name']:(field['select_choices_or_calculations'], field['field_type']) for field in metadata}#we need field_type for yes/no
    regex_full = r"\d+, [A-z0-9\s/%\-]+"#might need to modify the regex
    regex_num_choice = r"\d+,"
    regex_label_choice = r", [A-z0-9\s/%\-]+"
    for name in record_dict:
        if(name in name_choice_type and name_choice_type[name][0] != "" and record_dict[name] != ""):#we assume the values are not converted yet
            num_choice_lst = re.findall(regex_full, name_choice_type[name][0])#select_choices_or_calculations
            num_choice_lst = [choice.strip() for choice in num_choice_lst]#get rid of white spaces
            num_choices = [re.match(regex_num_choice, choice)[0].strip(" ,") for choice in num_choice_lst]
            label_choices = [re.search(regex_label_choice, choice)[0].strip(", ") for choice in num_choice_lst]
            for label_idx in range(len(label_choices)):
                if(record_dict[name] == label_choices[label_idx]):
                    record_dict[name] = num_choices[label_idx]
                    break
        elif(name in name_choice_type and name_choice_type[name][1] =="yesno" and record_dict[name] != ""):#special case of a multiple choice
            record_dict[name] = (lambda choice_name: '1' if choice_name == "Yes" else '0')(record_dict[name])

def get_options(field):
    """
    Given a field with types: radio or dropdwon function returns the options of the field.

    Parameters
    ----------
    field : dict
        Dictonary taken from the metadata list of dictonaries.

    Returns
    -------
    None.
    """
    regex = r",\s[\w\s/%-]+"
    options = [option.strip(", ") for option in re.findall(regex, field['select_choices_or_calculations'])]
    return options

def get_date():
    """
    Function today's date in the correct format.

    Parameters
    ----------
    None.

    Returns
    -------
    None.
    """
    today = datetime.date.today()
    date = str(today.year) +"-"+ str(today.month) + "-" + str(today.day)
    return date

def get_token(name_token):
    """
    Funtion reads token.txt file and uses corresponding to name_token token.

    Parameters
    ----------
    name_token : str
        Key corresponding to a token in token.txt file.

    Returns
    -------
    token : str
        Token corresponding to name_token.
    """
    token_dict = {}
    with open('token.txt','r') as token_file:
        token_dict = json.load(token_file)
    while True:
        try:
            return token_dict[name_token]
        except KeyError:
            print("The token for this user does not exist. Please Try again")
        name_token = input()

def getAllImages(folderPath):
    """
    Get all .png files in the folder located at folderPath.

    Parameters
    ----------
    folderPath : str
        Path of the folder where the images are located.

    Returns
    -------
    image_list : list
        A list of paths to the images.
    """
    image_list = []
    for file in os.listdir(folderPath):
        if file.endswith(".png"):
            image_list.append(os.path.join(folderPath, file))
    #make sure images are in the correct order 
    image_list.sort(key = lambda s: int(s[s.find("layer") + 5:s.find("layer") + 6]))
    return image_list

def getNumLayers(field_names, images):
    """
    Return number of layers.
    
    Parameters
    ----------
    field_names :  List-like iterbale
        An iterable that holds the names of the input fields.
    images : list
        A list of paths to the images.
    
    Returns
    -------
    min_layers : int
        Minimum number of layers that can be added to the experiment record.
    """
    layerNums = list(map(lambda elem: int(elem[elem.index("layer_") + 6:]) ,filter(lambda elem: elem.find("im_layer") != -1 , field_names)))

    min_layers = min(len(images), max(layerNums))

    return min_layers
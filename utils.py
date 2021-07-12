# utils.py is a good place to keep a bunch of helper functions

import os
from zipfile import ZipFile
import API_calls

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
    
def check_bran_logic(record_dict):
    """
    Eliminate the fields that are not supposed to be included in the record because their branching logic
    is not satisfied. 
    """
    metadata = API_calls.get_metadata()
    to_delete = []
    field_branch_logic = {field['field_name']:field['branching_logic'] for field in metadata}
    for field in record_dict:
        if not (field in field_branch_logic):
            continue
        logic = field_branch_logic[field]
        if(logic != ''):#then there is some logic that should be satisfied for this field
            field_w_logic = logic[logic.index('[')+1:logic.index(']')]#whatever is in square brackets
            values = [logic[index+ 3] for index, char in enumerate(logic) if char == '=']
            #Now, we need to check if field_w_logic have one of the specified values
            if (record_dict[field_w_logic] not in values):#if the logic is not satisfied by the required field, we delete the field
                to_delete.append(field)
    
    #Delete the selected keys
    for key in to_delete:
        del record_dict[key]

def convert_to_numeric(record_dict):
    metadata = API_calls.get_metadata()
    name_choice_type = {field['field_name']:(field['select_choices_or_calculations'], field['field_type']) for field in metadata}#we need field_type for yes/no
    for name in record_dict:
        if(name in name_choice_type and name_choice_type[name][0] != "" and record_dict[name] != ""):#we assume the values are not converted yet
            #pick a qualitative option and convert into a number, if someone have not inputted the number already
            #TODO: Probably need to make sure, we only have "label" options and not number options. Then, we wil defintely have to convert.
            num_choice = name_choice_type[name][0][name_choice_type[name][0].index(record_dict[name])-3]#here we operate under the assumption that the choices are single digits
            record_dict[name] = num_choice
        elif(name in name_choice_type and name_choice_type[name][1] =="yesno" and record_dict[name] != ""):#special case of a multiple choice
            record_dict[name] = (lambda choice_name: 1 if choice_name == "Yes" else 0)(record_dict[name])
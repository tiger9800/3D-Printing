# utils.py is a good place to keep a bunch of helper functions
import api_calls
import os
from zipfile import ZipFile
import re


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
    api = api_calls.API_calls()
    branch_dict = api.get_branching_dep_to_indep()
    to_delete = []
    
    # print("Here dependnent to independent dict:", branch_dict)
    for dependent_field in record_dict:
        to_delete_flag = False
        if(dependent_field in branch_dict):
            for independent_field in branch_dict[dependent_field]:
                #if the value that the indep fields takes satisfies the branching logic for the dependent, then do not delete
                # print("independent_field", independent_field)
                # print("dependent_field", dependent_field)
                # print("record_dict[independent_field]:", record_dict[independent_field]) 
                # print("(branch_dict[dependent_field][independent_field]", branch_dict[dependent_field][independent_field])
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
        print("Branching not satisfied:", key)
        del record_dict[key]

def convert_to_numeric(record_dict):
    api = api_calls.API_calls()
    metadata = api.get_metadata()
    name_choice_type = {field['field_name']:(field['select_choices_or_calculations'], field['field_type']) for field in metadata}#we need field_type for yes/no
    regex_full = "\d+, [A-z0-9\s/%\-]+"#might need to modify the regex
    regex_num_choice = "\d+,"
    regex_label_choice = ", [A-z0-9\s/%\-]+"
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
            # #pick a qualitative option and convert into a number, if someone have not inputted the number already
            # #TODO: Probably need to make sure, we only have "label" options and not number options. Then, we wil defintely have to convert.
            # print("Name:", record_dict[name])
            # #print("name_choice_type[name][0][name_choice_type[name][0]:", name_choice_type[name][0][name_choice_type[name][0])
            # num_choice = name_choice_type[name][0][name_choice_type[name][0].index(record_dict[name])-3]#here we operate under the assumption that the choices are single digits
        elif(name in name_choice_type and name_choice_type[name][1] =="yesno" and record_dict[name] != ""):#special case of a multiple choice
            record_dict[name] = (lambda choice_name: '1' if choice_name == "Yes" else '0')(record_dict[name])
import requests
import json
import utils

## This file could also use some refactoring
## I would suggest rename it into API calls (and make a class)
## make all the functions here associated only with API calls
## all other stuff can go to utils
## URL and token can be global variables or class fields as they are constant
## you can name the functions: post_trial and post_record (to reflect the http request)
## you can make functions post_trial and post_record smaller by extracting some logic to utils 

def get_metadata():
    """
    Returns the dictonary with metadata
    """
    payload = {"token" : "9063A3A857B5F42B3392C2C18320DE9E", "content":"metadata", "format":"json", "type":"flat"}
    URL = "https://redcap.crc.rice.edu/api/"
    response = requests.post(URL, data=payload)
    return response.json()



def add_record(user_input, printing_params):
    """
    This function  is for cretaion of a new records only (i.e. not a new trial)
    
    user_input - dictonary with the info user inputs through a form (i.e material info)
    printing_params - printing_parameters extracted from theinput file
    """
    #Let's get all the fields by running metadata
    metadata = get_metadata()
    #Create payload dict that will be us later
    payload = {"token" : "9063A3A857B5F42B3392C2C18320DE9E", "format":"json", "type":"flat"}
    URL = "https://redcap.crc.rice.edu/api/"
    record_print_mat = {field['field_name']: '' for field in metadata}#here we have all the fields from metadata
    #however, some should not be here if branching logic is not satisfied for them
    #before adding a field here, we have to 
    #Let's export instrument names
    payload['content'] = 'instrument'
    instruments = requests.post(URL, data=payload).json()
    for instrument in instruments:
        record_print_mat[instrument['instrument_name']+'_complete'] = ''
    #Now we have complete structures JSON literals with the correct key, but wihtout values
    for key in user_input:
        record_print_mat[key] = user_input[key]#record_id is included here
    utils.check_bran_logic(record_print_mat)
    utils.convert_to_numeric(record_print_mat)
    #Now we have completed the first two forms (should we updat _complete, or does user put it?)
    
    #Let's complete the third form(pritning parameters) form for the first trial
    record_print_params  = {field['field_name']: '' for field in metadata}#intialize the JSON literal
    #Let's add the instruments_complete'
    for instrument in instruments:
        record_print_params[instrument['instrument_name']+'_complete'] = ''#again, (should we update _complete?)
    record_print_params['record_id'] = record_print_mat['record_id']#the same record_id
    #We could use the API to get all the repeated instruments, but we have only one, so
    #we can just use it as the value
    record_print_params['redcap_repeat_instrument'] = 'printing_parameters'
    record_print_params['redcap_repeat_instance'] = 1 #we know it's the first trial
    #print("Here are printing params:", printing_params)
    for key in printing_params:#we can fill the rest using what we parsed from the export file
        record_print_params[key] = printing_params[key]
    utils.check_bran_logic(record_print_params)
    utils.convert_to_numeric(record_print_params)
    #Now, we just need to post the request
    print("here's printing printing_params dict passed as a parameter", printing_params)
    print("Here are record_print_params dict", record_print_params)
    payload['content'] = 'record'
    json_record = json.dumps([record_print_mat, record_print_params])
    payload['data'] = json_record
    
    #POST REQUEST FOR IMPORTING THE RECORD
    msg = requests.post(URL, data=payload)
    print(msg.json())
    assert(msg.json()['count'] == 1)

def add_trial(record_dict, printing_params):
    """
    This function adds a trial to an already existing experiment. In this case, user should have 
    inputed a valid record_id
    
    user_input - list of dictonaries associated with the
    record_id
    priniting_params - new printing params from the export file for the new trial
    """
    payload = {"token" : "9063A3A857B5F42B3392C2C18320DE9E", "content":"record", "format":"json", "type":"flat"}
    URL = "https://redcap.crc.rice.edu/api/"
    #We need to locate the record with the required record id
    #first establish max_value of the trial, redcap_repeat_instance and create redcap_repeat_instance = max_value + 1
    #We know we have max_value > =1 (from the prev function)
    max_value = max([sub_record['redcap_repeat_instance'] for sub_record in record_dict if sub_record['redcap_repeat_instance'] != ''])
    rep_instance = max_value + 1
    #now, let's create the new dict correcsponding to the new trial
    #record_dict[0] holds a dict with all the same keys
    record_print_params  = {key: '' for key in record_dict[0]}
    
    #Now, let's add "constant" vlaues
    record_print_params['record_id'] = record_dict[0]['record_id']#new trial, the record_id stays the same
    record_print_params['redcap_repeat_instrument'] = 'printing_parameters'

    #the rep instance
    record_print_params['redcap_repeat_instance'] = rep_instance
    #Finally, let's add the paramters of the new trial(parsed from export)
    
    for key in printing_params:
        record_print_params[key] = printing_params[key]
    metadata = get_metadata()
    utils.check_bran_logic(record_print_params)
    utils.convert_to_numeric(record_print_params)
    #POST REQUEST
    json_record = json.dumps([record_print_params])
    payload['data'] = json_record
    #POST REQUEST FOR IMPORTING THE RECORD(adding a new trial in this case)
    msg = requests.post(URL, data=payload)
    assert(msg.json()['count'] == 1)
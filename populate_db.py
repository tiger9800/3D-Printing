import requests
import json

def get_metadata():
    """
    Returns the dictonary with metadata
    """
    payload = {"token" : "9063A3A857B5F42B3392C2C18320DE9E", "content":"metadata", "format":"json", "type":"flat"}
    URL = "https://redcap.crc.rice.edu/api/"
    response = requests.post(URL, data=payload)
    return response.json()

def convert_to_numeric(record_dict, metadata):
    name_choice_type = {field['field_name']:(field['select_choices_or_calculations'], field['field_type']) for field in metadata}#we need field_type for yes/no
    for name in record_dict:
        if(name in name_choice_type and name_choice_type[name][0] != "" and record_dict[name] != ""):#we assume the values are not converted yet
            #pick a qualitative option and convert into a number, if someone have not inputted the number already
            #TODO: Probably need to make sure, we only have "label" options and not number options. Then, we wil defintely have to convert.
            num_choice = name_choice_type[name][0][name_choice_type[name][0].index(record_dict[name])-3]#here we operate under the assumption that the choices are single digits
            record_dict[name] = num_choice
        elif(name in name_choice_type and name_choice_type[name][1] =="yesno" and record_dict[name] != ""):#special case of a multiple choice
            record_dict[name] = (lambda choice_name: 1 if choice_name == "Yes" else 0)(record_dict[name])
def check_bran_logic(record_dict, metadata):
    """
    Eliminate the fields that are not supposed to be included in the record because their branching logic
    is not satisfied. 
    """
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
    check_bran_logic(record_print_mat, metadata)
    convert_to_numeric(record_print_mat, metadata)
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
    check_bran_logic(record_print_params, metadata)
    convert_to_numeric(record_print_params, metadata)
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
    check_bran_logic(record_print_params, metadata)
    convert_to_numeric(record_print_params, metadata)
    #POST REQUEST
    json_record = json.dumps([record_print_params])
    payload['data'] = json_record
    #POST REQUEST FOR IMPORTING THE RECORD(adding a new trial in this case)
    msg = requests.post(URL, data=payload)
    assert(msg.json()['count'] == 1)
import requests
import json
import utils
import re

class API_calls():
    URL = "https://redcap.crc.rice.edu/api/"
    token = ""
    #you could move this function to API calls
    def get_experiment_names(self):
        """
        Exports all the records from the API and to populate the list of the experiment names, used for
        new trials.
        """
        record_names = set()
        payload = {"token" : API_calls.token, "content":"record", "format":"json", "type":"flat"}
        URL = "https://redcap.crc.rice.edu/api/"
        response = requests.post(URL, data=payload)
        for json_lit in response.json():
            record_names.add(json_lit['record_id'])
        return list(record_names)#values["list"] does not have values if we give set as the values

    #this one too to API calls
    def get_elements(self, record_id):
        """
        Get all JSON literals(dicts) assocciated with the record_id.
        """
        #Could potentially just do one request.
        one_rec_lst = []
        payload = {"token" : API_calls.token, "content":"record", "format":"json", "type":"flat"}
        URL = "https://redcap.crc.rice.edu/api/"
        response = requests.post(URL, data=payload)
        for json_lit in response.json():
            if(json_lit['record_id'] == record_id):
                one_rec_lst.append(json_lit)
        return one_rec_lst
    def get_branching_dep_to_indep(self):
        """
        {dependent:{independent:set of values it can take}}
        """
        bran_dict = {}
        metadata = self.get_metadata()
        #regex to find all the strings of the format '[field_name] = '2''
        regex = "\[[A-z0-9]+\] = \'\d+\'"
        #Make a dictonary of the format{field_name {value: {set of fields that should be enabled when the value is picked}}}
        for field in metadata:
            if(field['branching_logic'] != "" and field['form_name'] == 'material_information'):#if a field has some branching logic and belongs to the correct instrument
                #get all fields that this field depend on
                logic_list = re.findall(regex, field['branching_logic'])
                #now we need to extract the names and values and for thet avlue
                for element in logic_list:
                    field_name = element[element.index('[')+1:element.index(']')]
                    value = element[element.index('\'')+1:element.index('\'', element.index('\'')+1)]
                    if(field['field_name'] not in bran_dict):
                        bran_dict[field['field_name']] = {field_name:set([value])}
                    else:#we already have some fields dependent on the field with field_name
                        if (field_name in bran_dict[field_name]):
                            bran_dict[field['field_name']][field_name].add(value)
                        else:#no such independent for this field yet
                            bran_dict[field['field_name']][field_name] = set([value])
        return bran_dict

    def get_branching_indep_to_dep(self):
        """
        Get the dictonary of branching logic. {independent (which enebales):{value :dependent(enabled by independening)}}
        """
        
        bran_dict = {}
        metadata = self.get_metadata()
        #regex to find all the strings of the format '[field_name] = '2''
        regex = "\[[A-z0-9]+\] = \'\d+\'"
        #Make a dictonary of the format{field_name {value: {set of fields that should be enabled when the value is picked}}}
        for field in metadata:
            if(field['branching_logic'] != "" and field['form_name'] == 'material_information'):#if a field has some branching logic and belongs to the correct instrument
                #get all fields that this field depend on
                logic_list = re.findall(regex, field['branching_logic'])
                #now we need to extract the names and values and for thet avlue
                for element in logic_list:
                    field_name = element[element.index('[')+1:element.index(']')]
                    value = element[element.index('\'')+1:element.index('\'', element.index('\'')+1)]
                    if(field_name not in bran_dict):
                        bran_dict[field_name] = {value:set([field['field_name']])}
                    else:#we already have some fields dependent on the field with field_name
                        if (value in bran_dict[field_name]):
                            bran_dict[field_name][value].add(field['field_name'])
                        else:#no such value for this field yet
                            bran_dict[field_name][value] = set([field['field_name']])
        return bran_dict
    def get_instruments(self):
        payload = {"token" : API_calls.token, "format":"json", "type":"flat", "content":"instrument"}
        instruments = requests.post(API_calls.URL, data=payload).json()
        return instruments

    def get_metadata(self):
        """
        Returns the dictonary with metadata
        """
        payload = {"token" : API_calls.token, "content":"metadata", "format":"json", "type":"flat"} 
        response = requests.post(API_calls.URL, data=payload)
        return response.json()

    def add_record(self, user_input, printing_params):
        """
        This function is for cretaion of a new records only (i.e. not a new trial).
        
        user_input - dictonary with the info user inputs through a form (i.e material info)
        printing_params - printing_parameters extracted from theinput file
        """
        #Let's get all the fields by running metadata
        metadata = self.get_metadata()
        #Create payload dict that will be us later
        payload = {"token" : API_calls.token, "format":"json", "type":"flat"}
        record_print_mat = {field['field_name']: '' for field in metadata}#here we have all the fields from metadata
        #Let's export instrument names
        instruments = self.get_instruments()
        for instrument in instruments:
            record_print_mat[instrument['instrument_name']+'_complete'] = ''
        #Now we have complete structures JSON literals with the correct key, but wihtout values
        for key in user_input:
            record_print_mat[key] = user_input[key]#record_id is included here
        record_print_mat['material_information_complete'] = '2'
        record_print_mat['printer_information_complete'] = '2'
       
        utils.convert_to_numeric(record_print_mat)
        utils.check_bran_logic(record_print_mat)
        if('paxton' in record_print_mat):
            del record_print_mat['paxton']#cause an error when Gels are selected alternatively we could delete
        #the field from the survey

        #Now we have completed the first two forms (should we updat _complete, or does user put it?)
        #Let's complete the third form(pritning parameters) form for the first trial
        record_print_params  = {field['field_name']: '' for field in metadata}#intialize the JSON literal
        #Let's add the instruments_complete'
        for instrument in instruments:
            record_print_params[instrument['instrument_name']+'_complete'] = ''
        record_print_params['printing_parameters_complete'] = '2'

        record_print_params['record_id'] = record_print_mat['record_id']#the same record_id
        #We could use the API to get all the repeated instruments, but we have only one, so
        #we can just use it as the value
        record_print_params['redcap_repeat_instrument'] = 'printing_parameters'
        record_print_params['redcap_repeat_instance'] = 1 #we know it's the first trial
        record_print_params['date_exp']= utils.get_date()
        #print("Here are printing params:", printing_params)
        for key in printing_params:#we can fill the rest using what we parsed from the export file
            record_print_params[key] = printing_params[key]
        utils.convert_to_numeric(record_print_params)
        utils.check_bran_logic(record_print_params)
        #Now, we just need to post the request
        payload['content'] = 'record'
        json_record = json.dumps([record_print_mat, record_print_params])
        payload['data'] = json_record
        
        #POST REQUEST FOR IMPORTING THE RECORD
        msg = requests.post(API_calls.URL, data=payload)
        if('error' in msg.json()):
            print(msg.json())
            print(msg.json()['erorr'])
    

    def add_trial(self, record_dict, printing_params):
        """
        This function adds a trial to an already existing experiment. In this case, user should have 
        inputed a valid record_id
        
        user_input - list of dictonaries associated with the
        record_id
        priniting_params - new printing params from the export file for the new trial
        """
        payload = {"token" : API_calls.token, "content":"record", "format":"json", "type":"flat"}
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
        record_print_params['date_exp']= utils.get_date()
        for key in printing_params:
            record_print_params[key] = printing_params[key]

        #Indicate that forms are complete
        instruments = self.get_instruments()

        for instrument in instruments:
            record_print_params[instrument['instrument_name']+'_complete'] = ''
        
        record_print_params['printing_parameters_complete'] = '2'
        #make the form complete
        utils.check_bran_logic(record_print_params)
        utils.convert_to_numeric(record_print_params)
        #POST REQUEST
        json_record = json.dumps([record_print_params])
        payload['data'] = json_record
        #POST REQUEST FOR IMPORTING THE RECORD(adding a new trial in this case)
        msg = requests.post(API_calls.URL, data=payload)
        if('error' in msg.json()):
            print(msg.json())
            print(msg.json()['erorr'])
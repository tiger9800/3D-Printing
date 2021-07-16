import requests
import json
import utils
import re

## This file could also use some refactoring
## I would suggest rename it into API calls (and make a class)
## make all the functions here associated only with API calls
## all other stuff can go to utils
## URL and token can be global variables or class fields as they are constant
## you can name the functions: post_trial and post_record (to reflect the http request)
## you can make functions post_trial and post_record smaller by extracting some logic to utils 
class API_calls():
    token = "9063A3A857B5F42B3392C2C18320DE9E"
    URL = "https://redcap.crc.rice.edu/api/"

    #you could move this function to API calls
    def get_experiment_names(self):
        """
        Exports all the records from the API and to populate the list of the experiment names, used for
        new trials.
        """
        record_names = set()
        payload = {"token" : "9063A3A857B5F42B3392C2C18320DE9E", "content":"record", "format":"json", "type":"flat"}
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
        payload = {"token" : "9063A3A857B5F42B3392C2C18320DE9E", "content":"record", "format":"json", "type":"flat"}
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
    def get_metadata(self):
        """
        Returns the dictonary with metadata
        """
        payload = {"token" : self.token, "content":"metadata", "format":"json", "type":"flat"} 
        response = requests.post(self.URL, data=payload)
        return response.json()



    def add_record(self, user_input, printing_params):
        """
        This function  is for cretaion of a new records only (i.e. not a new trial)
        
        user_input - dictonary with the info user inputs through a form (i.e material info)
        printing_params - printing_parameters extracted from theinput file
        """
        #Let's get all the fields by running metadata
        metadata = self.get_metadata()
        #Create payload dict that will be us later
        payload = {"token" : self.token, "format":"json", "type":"flat"}
        record_print_mat = {field['field_name']: '' for field in metadata}#here we have all the fields from metadata
        #Let's export instrument names
        payload['content'] = 'instrument'
        instruments = requests.post(self.URL, data=payload).json()
        for instrument in instruments:
            record_print_mat[instrument['instrument_name']+'_complete'] = ''
        #Now we have complete structures JSON literals with the correct key, but wihtout values
        for key in user_input:
            record_print_mat[key] = user_input[key]#record_id is included here
       
        # print("here's printing user_input dict passed as a parameter (before check_bran_logic)", user_input)
        # print("Here are record_print_mat dict (before check_bran_logic)", record_print_mat)
        utils.convert_to_numeric(record_print_mat)
        utils.check_bran_logic(record_print_mat)
        if('paxton' in record_print_mat):
            del record_print_mat['paxton']#cause an error when Gels are selected alternatively we could delete
        #the field from the survey

        #Now we have completed the first two forms (should we updat _complete, or does user put it?)
        # print("here's printing user_input dict passed as a parameter (after check_bran_logic)", user_input)
        # print("Here are record_print_mat dict (after check_bran_logic)", record_print_mat)
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
        utils.convert_to_numeric(record_print_params)
        utils.check_bran_logic(record_print_params)
        #Now, we just need to post the request
        # print("here's printing printing_params dict passed as a parameter", printing_params)
        # print("Here are record_print_params dict", record_print_params)
        payload['content'] = 'record'
        json_record = json.dumps([record_print_mat, record_print_params])
        payload['data'] = json_record
        
        #POST REQUEST FOR IMPORTING THE RECORD
        msg = requests.post(self.URL, data=payload)
        if('error' in msg.json()):
            print(msg.json()['erorr'])
        # print(msg.json())
        # assert(msg.json()['count'] == 1)

    def add_trial(self, record_dict, printing_params):
        """
        This function adds a trial to an already existing experiment. In this case, user should have 
        inputed a valid record_id
        
        user_input - list of dictonaries associated with the
        record_id
        priniting_params - new printing params from the export file for the new trial
        """
        payload = {"token" : self.token, "content":"record", "format":"json", "type":"flat"}
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
        utils.check_bran_logic(record_print_params)
        utils.convert_to_numeric(record_print_params)
        #POST REQUEST
        json_record = json.dumps([record_print_params])
        payload['data'] = json_record
        #POST REQUEST FOR IMPORTING THE RECORD(adding a new trial in this case)
        msg = requests.post(self.URL, data=payload)
        if('error' in msg.json()):
            print(msg.json()['erorr'])
        # assert(msg.json()['count'] == 1)
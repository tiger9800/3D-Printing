import requests
import json
import utils
import re
import redcap

class API_calls:
    """
    Class used for interacting with REDCap API through POST requests.
    """
    URL = "https://redcap.crc.rice.edu/api/"
    token = ""
    #you could move this function to API calls
    def get_experiment_names(self):
        """
        Methods that returns set of record_id's present in the REDCap project.

        Parameters
        ----------
        None.

        Returns
        -------
        record_names : set
            A set of record_id's/experiments. 
        """
        record_names = set()
        payload = {"token" : API_calls.token, "content":"record", "format":"json", "type":"flat"}
        URL = "https://redcap.crc.rice.edu/api/"
        response = requests.post(URL, data=payload)
        for json_lit in response.json():
            record_names.add(json_lit['record_id'])
        return record_names

    #this one too to API calls
    def get_elements(self, record_id):
        """
        Method that returns all JSON literals(dicts) assocciated with the record_id.

        Parameters
        ---------- 
        record_id : str
            String corresponding to the record_id for an experiment.

        Returns
        -------
        one_rec_lst : list
            List containg all JSON literals(dicts) that have record_id.
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
        Method that returns a dictonary of the form {dependent field :{independent field:set of values independent can take to triger the
        the dependent field appearance.

        Parameters
        ----------
        None.

        Returns
        -------
        bran_dict : dict 
            Dictonary with the branching logic.
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
        Method that returns a dictonary of the form {independent field :{dependent field:set of values independent field
        can take to triger the the dependent field appearance.}}

        Parameters
        ----------
        None.

        Returns
        -------
            bran_dict : dict with the branching logic.
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
        """
        Methods that returns the a list of instruments from the REDCap project.

        Parameters
        ----------
        None.

        Returns
        -------
        instruments : list
            List containing instruments from the REDCap project.
        """

        payload = {"token" : API_calls.token, "format":"json", "type":"flat", "content":"instrument"}
        instruments = requests.post(API_calls.URL, data=payload).json()
        return instruments

    def get_metadata(self):
        """
        Method that returns the dictonary with metadata.

        Parameters
        ----------
        None.

        Returns
        -------
        metadata : dict
            Dictonary containing metadata.

        """
        payload = {"token" : API_calls.token, "content":"metadata", "format":"json", "type":"flat"} 
        response = requests.post(API_calls.URL, data=payload)
        metadata = response.json()
        return metadata

        

    def importImages(self, record_id, repeat_instance, num_images, images):
        
        """ 
        Method that imports all images into the REDCap project for the specified record_id.

        Parameters
        ----------
        record_id : str
            The record_id associated with the print for which images were taken.
        repeat_instance : str
            The trial for which images were taken.
        num_images : int
            The number of images/layers.
        images : list
            List of the paths of the images.

        Returns
        -------
        None.
        """
        
        project = redcap.Project(API_calls.URL, API_calls.token)
        
        for num_img in range(1, num_images + 1):
            fname = images[num_img-1]
            with open(fname, 'rb') as fobj:
                project.import_file(record=record_id, field = 'im_layer_'+str(num_img), fname = fname, fobj = fobj, repeat_instance=repeat_instance)
        

    def add_record(self, user_input, printing_params, folderPath):
        """
        Method that adds a record about a new experiment to the REDCap Project. 
        
        Parameters
        ----------
        user_input : dict
            Dictonary with the info user inputted through the GUI form (i.e material info).
        printing_params : dict
            Dictonary with printing_parameters extracted from the XML file.

        Returns
        -------
        None.
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

        #Now we have completed the first two forms
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

        #get number of images/layers

        images = utils.getAllImages(folderPath)
        if len(images) != 0:
            num_layers = utils.getNumLayers(record_print_params.keys(), images)
            record_print_params['num_layers'] = num_layers
        #Now, we just need to post the request
        payload['content'] = 'record'
        json_record = json.dumps([record_print_mat, record_print_params])
        payload['data'] = json_record
        
        #POST REQUEST FOR IMPORTING THE RECORD
        msg = requests.post(API_calls.URL, data=payload)
        if('error' in msg.json()):
            print(msg.json())
            print(msg.json()['erorr'])

        #add images
        if len(images) != 0:
            self.importImages(record_print_params['record_id'], 1, num_layers, images)
    

    def add_trial(self, record_dict, printing_params, folderPath):
        """
        Method that adds a new trial to an existing experiment to the REDCap Project. 
        
        Parameters
        ----------
        record : dict
            Dictonary with the info user inputted through the GUI form when performing the first trial of the experiment.
        printing_params : dict
            Dictonary with printing_parameters extracted from the XML file.
        
        Returns
        -------
        None.
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
        #Finally, let's add the params of the new trial(parsed from export)
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

        images = utils.getAllImages(folderPath)
        if len(images) != 0:
            num_layers = utils.getNumLayers(record_print_params.keys(), images)
            record_print_params['num_layers'] = num_layers

        #POST REQUEST
        json_record = json.dumps([record_print_params])
        payload['data'] = json_record
        #POST REQUEST FOR IMPORTING THE RECORD(adding a new trial in this case)
        msg = requests.post(API_calls.URL, data=payload)
        if('error' in msg.json()):
            print(msg.json())
            print(msg.json()['erorr'])

        #add images
        if len(images) != 0:
            self.importImages(record_print_params['record_id'], rep_instance, num_layers, images)
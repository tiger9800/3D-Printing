import re
from subprocess import check_call
import PySimpleGUI as sg
from PySimpleGUI.PySimpleGUI import Text
import api_calls
import utils
import copy

class GUI():
    """
    Class responsible for creating GUI, collecting and validating user-inputted data.
    """

    api = api_calls.API_calls()
    def clear_disable_all(self, window, branch_log_dict, to_clear):
        """
        Methods that clears the fields and disables all the fields that depend on branching logic.
        Invoked by the radio button.

        Parameters
        ----------
        window : dict
            Dictonary maintained by PySimpleGUI to store information about the GUI window.
        branch_log_dict : dict
            Dictonary with the branching logic.
        to_disable : fields to 

        to_clear : list
            List of lists with elements to clear.
        """
        #let's first clear all the fields
        for row in to_clear:
            for elem in row:
                if(elem.metadata != 'not_disable' and not isinstance(elem, sg.Text) and not isinstance(elem, sg.Listbox)):#do not block the radio button):
                    window[elem.Key].update(value = "")

        #let's now disable the branching logic
        keys_to_disable = set()
        for element in branch_log_dict:
            for value in branch_log_dict[element]:
                keys_to_disable.update(branch_log_dict[element][value])
        for element in keys_to_disable:
            if(not isinstance(window[element], sg.Text)):
                window[element].update(disabled = True)
                window[element].metadata = False


    def enable_selected(self, window, values, branch_log_dict, key_event):
        """
        Method that enables the elements that can be used because a conditon in 
        branching logic is satisfied.
        Invoked when we change an option on which the branching logic depends.

        Parameters
        ----------
        window : dict
            Dictonary maintained by PySimpleGUI to store information about the GUI window.
        values : dict
            Dictonary with current values of the elements in the GUI.
        branch_log_dict : dict
            Dictonary with the branching logic.
        key_event : str
            Key of the elements that triggered call of the method.

        """
        utils.convert_to_numeric(values)
        if(values[key_event] in branch_log_dict[key_event]):#if there is branching for the chosen option
            for element_key in branch_log_dict[key_event][values[key_event]]:
                #values the element can take
                if not isinstance(window[element_key], sg.Text):
                    window[element_key].update(disabled = False)
                    window[element_key].metadata = True
                    window[element_key+"_label"].update(text_color = "#FFFFFF")#every non-text field has a label
                window[element_key].update(visible = True)
                
    def disable_not_selected(self, window, values, branch_log_dict, key_event):
        """
        Method that disables the elements that cannot be used because of a conditon in 
        branching logic that is not satisfied.

        Parameters
        ----------
        window : dict
            Dictonary maintained by PySimpleGUI to store information about the GUI window.
        values : dict
            Dictonary with current values of the elements in the GUI.
        branch_log_dict : dict
            Dictonary with the branching logic.
        key_event : str
            Key of the elements that triggered call of the method.
        """
        #we need to convert values[element] into the numeric
        #could used deepcopy, but we do not actually need it
        utils.convert_to_numeric(values)
        key_set = set(branch_log_dict[key_event].keys())
        for key in key_set.difference(set([values[key_event]])):
            for element_key in branch_log_dict[key_event][key]:
                if not isinstance(window[element_key], sg.Text) and not isinstance(window[element_key], sg.Listbox):
                    window[element_key].update(disabled = True)
                    window[element_key].update(value = "")
                    window[element_key].metadata = False
                    window[element_key+"_label"].update(text_color = "#000000")#every non-text field has a label
                window[element_key].update(visible = False)
    def make_fields(self):
        """
        Method Creates a list of lists(where each inner list is a row). Each row consists of fields
        """
        #Let's first get fields in material_information printer_information
        metadata = GUI.api.get_metadata()
        field_correct_form = filter(lambda field: field['form_name']=='material_information' or field['form_name'] == 'printer_information', metadata)
        rows_w_fields = []
        for field in field_correct_form:
            #make label
            row = []
            key = field['field_name']
            type = field['field_type']
            row.append(sg.Text(text = field['field_label'], key=key+"_label"))#keys for labels are key_label (ex. record_id_label)
            if(type == 'radio' or type == "dropdown"):
                options = utils.get_options(field)
                row.append(sg.Combo(options, key=key, disabled= True, metadata=True, enable_events=True))
            elif(type == "yesno"):
                options = ["Yes", "No"]
                row.append(sg.Combo(options, key=key, disabled= True, metadata=True, enable_events=True))
            elif(type == "text"):
                row.append(sg.Input(key=key, disabled=True, metadata=True))
            else:#descirptive
                row[0] = sg.Text(text = field['field_label'], key=key, metadata=True)#we only need text in this case
            rows_w_fields.append(row)
        return rows_w_fields  

    def validate_fields(self, window, values):
        """
        Method that validates fields according to the validation specified in the REDCap project and 
        prevents creation of new experiments with existing record_id record.

        Returns 
        --------

        is_valid : bool
            Boolean indicating if all fields pass the validation.
        problem_field_name : str
            Label of a field that failed validation. Default "".
        record_lst : list
            List of dictonaries corresponding to an experiment.
        
        """
        
        #Check if record id is new
        is_valid = True
        problem_field_name = ""
        experiment_names = GUI.api.get_experiment_names()
        if values['record_id'] in experiment_names:
            is_valid = False
            problem_field_name = "Record ID"
            return is_valid, problem_field_name 
        
        metadata = GUI.api.get_metadata()
        enbaled_fields = filter(lambda elem: (elem['form_name']=='material_information' or elem['form_name']=='printer_information') 
        and not (isinstance(window[elem['field_name']], sg.Text) or window[elem['field_name']].Disabled), metadata)#only validate enbaled fields
        for field in enbaled_fields:
            validation = field['text_validation_type_or_show_slider_number']
            value = values[field['field_name']]
            if (validation == "number" and value.isdigit()):
                #check if correct ranges
                if field['text_validation_max'] != "":
                    if value > field['text_validation_max']:
                        is_valid = False 
                        problem_field_name = field['field_label']
                        return is_valid, problem_field_name  
                if field['text_validation_min'] != "":
                    if value < field['text_validation_min']:
                        is_valid = False 
                        problem_field_name = field['field_label']
                        return is_valid, problem_field_name      
            elif (validation == "number" and not value.isdigit()):
                is_valid = False
                problem_field_name = field['field_label']
                return is_valid, problem_field_name
        return is_valid, problem_field_name
    def get_print_result(self):
        """
        Method that converts the user-response on the popup into a valid REDCap response.
        """
        return "Good Print" if sg.popup_yes_no("Is it a good print?", title = "Print Quality") == "Yes" else "Bad Print"
        
    def getPicturesPrintEval(self):

        col_print_quality = [[sg.Radio('Good Print', "Print Quality", default=True, enable_events = True, key="good_radio", metadata='not_disable')],
        [sg.Radio('Bad Print', "Print Quality", default=False, enable_events = True, key="bad_radio", metadata='not_disable')],
        [sg.Text("Please input your comments (if any): "),sg.Multiline()],
        [sg.Button(button_text= "OK", enable_events= True, key ="OK")]]

        col_images =  [[sg.Text("Folder with Images Location:")], 
        [sg.Input(key = "FolderName"), sg.FolderBrowse(button_text = "Browse")]]
        layout =  [[sg.Column(col_print_quality), sg.Column(col_images)]]
       
        

        window = sg.Window('Print Assesment', layout, keep_on_top=True)#Creation of the window
        while True:
            event, values = window.read()
            # End program if user closes window or
            # presses the OK button
            # you can use switch-case here instead of if statements
            if event == sg.WIN_CLOSED:
                #Indicate abort
                window.close()
                return ("Good Print", None) if values["good_radio"] else ("Bad Print", None)
            elif event == "OK":
                fileName = values["FolderName"]
                window.close()
                return ("Good Print", fileName) if values["good_radio"] else ("Bad Print", fileName)

            
    def start_GUI(self):
        """
        Method where the main GUI logic is implemented. 
        
        Returns
        -------
        func_name : str
            Name of the action to perform with the data received
        record_lst 
        print_result : str
            Result of the response to the "print quality" popup.
        return "add_trial", record_lst, print_result
        
        """
        experiment_names = list(GUI.api.get_experiment_names())
        #selected_exp = None #value picked in the list

        branch_log_dict = GUI.api.get_branching_indep_to_dep()
        #Separate columns for a new trial and a new experiment

        col_new_trial = [[sg.Radio('New Trial', "RADIO1", default=True, enable_events = True, key="new_trial_radio", metadata='not_disable')],
        [sg.Text(text = "Please pick your experiment from the list below:")], 
        [sg.Listbox(values=experiment_names, size=(30, 6), key="list", select_mode = sg.LISTBOX_SELECT_MODE_SINGLE, enable_events= True)]]
        

        #metadata ahs true if we need to input filed
        col_new_experiment = [[sg.Radio('New experiment', "RADIO1", enable_events=True, key="new_exp_radio", metadata='not_disable')]]
        col_new_experiment.extend(self.make_fields())#add fields to the form
        layout =  [[sg.Column(col_new_trial), sg.Column(col_new_experiment)], 
        [sg.Button(button_text= "OK", enable_events= True, key ="OK")]]
   
        window = sg.Window('New Data', layout, keep_on_top=True)#Creation of the window
        while True:
            event, values = window.read()
            # End program if user closes window or
            # presses the OK button
            # you can use switch-case here instead of if statements
            if event == sg.WIN_CLOSED:
                #Indicate abort
                return None, None, None
            elif event == "new_exp_radio":#if new experiment is picked, then disable the elements for the new trial
                #for evey field on which branching logic depends on, disable everything not selected
                window['list'].update(disabled = True)
                for row in col_new_experiment:
                    for elem in row:
                        if(elem.metadata != 'not_disable' and not isinstance(elem, sg.Text)):#do not block the radio button):
                            window[elem.Key].update(disabled = False)
                
                self.clear_disable_all(window, branch_log_dict, col_new_experiment)#we could just enable a few, instead
            elif event == "new_trial_radio":#if new trial is picked, disable the elements for the new experiment, enable for the new trua
                #disable everything in the form
                for row in col_new_experiment:
                    for elem in row:
                        if(elem.metadata != 'not_disable' and not isinstance(elem, sg.Text)):#do not block the radio button and do not update textboxes
                            window[elem.Key].update(disabled = True)
                #enable the listbox
            
                window['list'].update(disabled = False)
            elif event == "OK":
                field_missing = False
                #Check if the listbox has a value or the form has a value
                if values['new_exp_radio']:#we are doing new expriment
                    # printing_params = {"paxton":""}
                    printing_params = {}
                    #Check the all the stuff in the form of the new experiment
                    for row in col_new_experiment:
                        if(field_missing):
                            break#do not check anymore
                        for elem in row:
                            if(elem.metadata != 'not_disable' and not isinstance(elem, sg.Text)):#do not check labels and the radio button
                                if (elem.metadata and values[elem.Key]== ""): #value ahs to be filled and not empty
                                    field_missing = True
                                    sg.popup_ok('Required fields are missing!')#if at least one field is empty, throw a popup and stop checking
                                    break  # Shows OK button
                                    #if at least one field does not have a value, then we generate a popup
                                elif(values[elem.Key] != ""):#add to the dictonary of paramaters
                                    printing_params[elem.Key] = values[elem.Key]
                       
                    if not field_missing:
                        #if everything is filled, then validate
                        
                        #if user closes the popup, then the print is considered bad by default
                        is_valid, field_name = self.validate_fields(window, values)
                        if(is_valid):
                            print_result, folderPath = self.getPicturesPrintEval()
                            window.close()
                            #now, we also return print_result
                            return "add_record", printing_params, print_result, folderPath
                        else:
                            sg.popup_ok("The field could not be validated: " + field_name)
                                                        
                elif values['new_trial_radio']:#could use else
                    if values['list'] == []:
                        sg.popup_ok('Required fields are missing!')
                        continue#go to while loop
                    #we got here, so we now know the record_id of the experiment we want to do the new trial for
                    record_lst = GUI.api.get_elements(values['list'][0])
                    #create a new window with print quality + pictures
                    print_result, folderPath = self.getPicturesPrintEval()
                    window.close()
                    return "add_trial", record_lst, print_result, folderPath
            elif event in branch_log_dict:#if branching logic is dependent on this element
                #we could only enable/disable stuff affected by the element
                self.enable_selected(window, copy.deepcopy(values), branch_log_dict, event)
                self.disable_not_selected(window, copy.deepcopy(values), branch_log_dict, event)

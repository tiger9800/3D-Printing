import re
from subprocess import check_call
import PySimpleGUI as sg
from PySimpleGUI.PySimpleGUI import Text
import api_calls
import utils
import copy

class GUI():
    api = api_calls.API_calls()
    def clear_disable_all(self, window, branch_log_dict, to_disable, caller_key = "new_exp_radio"):
        """
        Clears the fields and disables all the fields that depend on branching logic.
        Invoked by the radio button.

        to_disable - list of rows with elements to clear
        """
        #let's first clear all the fields
        for row in to_disable:
            for elem in row:
                if(elem.metadata != 'not_disable' and not isinstance(elem, sg.Text)):#do not block the radio button):
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
        Enable the elements that can be used because a conditon in 
        branching logic is satisfied.
        Invoked when we change an option on which the branching logic depends.
        """
        utils.convert_to_numeric(values)
        # print("Here is branch_log_dict:", branch_log_dict)
        # print("Here is values:", values)
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
        Disable the elements that cannot be used because of a conditon in 
        branching logic not being satisfied.
        Invoked when we change an option on which the branching logic depends.
        """
        #we need to convert values[element] into the numeric
        #could used deepcopy, but we do not actually need it
        utils.convert_to_numeric(values)
        key_set = set(branch_log_dict[key_event].keys())
        for key in key_set.difference(set([values[key_event]])):
            for element_key in branch_log_dict[key_event][key]:
                if not isinstance(window[element_key], sg.Text):
                    window[element_key].update(disabled = True)
                    window[element_key].update(value = "")
                    window[element_key].metadata = False
                    window[element_key+"_label"].update(text_color = "#000000")#every non-text field has a label
                window[element_key].update(visible = False)
    def make_fields(self):
        """
        Creates a list of lists(where each inner list is a row). Each row consists of fields
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
        Validate fields according to the validation specified in REDCap.

        Returns True/False as the first element of a tuple to indicate if the fields passed validation
        """
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
                        return False, field['field_label']
                if field['text_validation_min'] != "":
                    if value < field['text_validation_min']:
                        return False, field['field_label']
                    
            elif (validation == "number" and not value.isdigit()):
                print("number but not digit")
                return False, field['field_label']
        return True, None
    def get_print_result(self):
        return "Good Print" if sg.popup_yes_no("Is it a good print?", title = "Print Quality") == "Yes" else "Bad Print"
        
    def start_GUI(self):
        """
        Does everything related to do the UI. Returns the type of the action to do and the other required parameter. In other words, 
        add a new trial or add a new experiment.
        
        """
        experiment_names = GUI.api.get_experiment_names()
        branch_log_dict = GUI.api.get_branching_indep_to_dep()
        #Separate columns for a new trial and a new experiment

        col_new_trial = [[sg.Radio('New Trial', "RADIO1", default=True, enable_events = True, key="new_trial_radio", metadata='not_disable')],
        [sg.Text(text = "Please pick your experiment from the list below:")], 
        [sg.Listbox(values=experiment_names, size=(30, 6), key="list", select_mode = sg.LISTBOX_SELECT_MODE_SINGLE)]]

        #metadata ahs true if we need to input filed
        col_new_experiment = [[sg.Radio('New experiment', "RADIO1", enable_events=True, key="new_exp_radio", metadata='not_disable')]]
        col_new_experiment.extend(self.make_fields())#add fields to the form
        layout =  [[sg.Column(col_new_trial), sg.Column(col_new_experiment)], 
        [sg.Button(button_text= "OK", enable_events= True, key ="OK")]]
   
        window = sg.Window('New Data', layout)
        while True:
            event, values = window.read()
            # End program if user closes window or
            # presses the OK button
            # you can use switch-case here instead of if statements
            if event == sg.WIN_CLOSED:
                #LIndicate abort
                return None, None, None
            elif event == "new_exp_radio":#if new experiment is picked, then disable the elements for the new trial
                #for evey field on which branching logic depends on, disable everything not selected
                window['list'].update(disabled = True)
                for row in col_new_experiment:
                    for elem in row:
                        if(elem.metadata != 'not_disable' and not isinstance(elem, sg.Text)):#do not block the radio button):
                            window[elem.Key].update(disabled = False)
                # print("I am here (new_exp_radio)")
                self.clear_disable_all(window, branch_log_dict, col_new_experiment)#we could just enable a few, instead
            elif event == "new_trial_radio":#if new trial is picked, diable the element fir the new experiment, enable for the new trua
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
                        
                        # print("Here are printing_params in GUI_code.py:", printing_params)
                        #if user closes the popup, then the print is considered bad by default
                        is_valid, field_name = self.validate_fields(window, values)
                        if(is_valid):
                            print_result = self.get_print_result()
                            window.close()
                            #now, we also return print_result
                            return "add_record", printing_params, print_result
                        else:
                            sg.popup_ok("The field could not be validated: " + field_name)
                                                        
                elif values['new_trial_radio']:#could use else
                    # print("here are values of list_box", values['list'])
                    # print("here are values:", values)
                    if values['list'] == []:
                        sg.popup_ok('Required fields are missing!')
                        continue#go to while loop
                    #we got here, so we now know the record_id of the experiment we want to do the new trial for
                    record_lst = GUI.api.get_elements(record_id=values['list'][0])
                    print_result = self.get_print_result()
                    window.close()
                    return "add_trial", record_lst, print_result
            elif event in branch_log_dict:#if branching logic is dependent on this element
                #we could only enable/disable stuff affected by the element
                self.enable_selected(window, copy.deepcopy(values), branch_log_dict, event)
                self.disable_not_selected(window, copy.deepcopy(values), branch_log_dict, event)
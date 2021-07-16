import PySimpleGUI as sg
import api_calls
import utils
import copy

class GUI():
    def clear_disable_all(self, window, branch_log_dict, to_disable, caller_key = "new_exp_radio"):
        """
        Clears the fields and disables all the fields that depend on branching logic.
        Invoked by the radio button.

        to_disable - list of rows with elements to clear
        """
        #let's first clear all the fields
        for row in to_disable:
            for elem in row:
                if(elem.Key != None and elem.metadata != 'not_disable'):#do not block the radio button):
                    window[elem.Key].update(value = "")

        #let's now disable the branching logic
        keys_to_disable = set()
        for element in branch_log_dict:
            for value in branch_log_dict[element]:
                keys_to_disable.update(branch_log_dict[element][value])
        for element in keys_to_disable:
            if(element!="paxton"):
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
            for element in branch_log_dict[key_event][values[key_event]]:
                #values the element can take
                # print("Enable:", element)
                if(element!= "paxton"):#could do differently
                    window[element].update(disabled = False)
                    window[element].metadata = True
                window[element].update(visible = True)
    def disable_not_selected(self, window, values, branch_log_dict, key_event=None):
        """
        Disable the elements that cannot be used because of a conditon in 
        branching logic not being satisfied.
        Invoked when we change an option on which the branching logic depends.
        """
        #we need to convert values[element] into the numeric
        #could used deepcopy, but we do not actually need it
        utils.convert_to_numeric(values)
        key_set = set(branch_log_dict[key_event].keys())
        # print("Here is branch_log_dict:", branch_log_dict)
        #Here values dict is already modified, so we get a different result(before deepcopy)
        # print("Here is values:", values)
        # print("Here's key_event:", key_event)
        # print("Here is key_set", key_set)
        # print("Here's the key elements of which we do not want to disable:", values[key_event])
        # print("Here's the set of values to disable(difference):", key_set.difference(set([values[key_event]])))
        for key in key_set.difference(set([values[key_event]])):
            for element in branch_log_dict[key_event][key]:
                # print("Disable:", element)
                if(element!= "paxton"):#could do differently
                    window[element].update(disabled = True)
                    window[element].update(value = "")
                    window[element].metadata = False
                window[element].update(visible = False)
    def start_GUI(self):
        """
        Does everything related to do the UI. Returns the type of the action to do and the other required parameter. In other words, 
        add a new trial or add a new experiment.
        
        """

        api = api_calls.API_calls()
        experiment_names = api.get_experiment_names()
        branch_log_dict = api.get_branching_indep_to_dep()
        #Separate columns for a new trial and a new experiment
        col_new_trial = [[sg.Radio('New Trial', "RADIO1", default=True, enable_events = True, key="new_trial_radio", metadata='not_disable')],
        [sg.Text(text = "Please pick your experiment from the list below:")], 
        [sg.Listbox(values=experiment_names, size=(30, 6), key="list", select_mode = sg.LISTBOX_SELECT_MODE_SINGLE)]]

        #metadata ahs true if we need to input filed
        col_new_experiment = [[sg.Radio('New experiment', "RADIO1", enable_events=True, key="new_exp_radio", metadata='not_disable')], 
        [sg.Text(text = "RecordID:"), sg.Input(key='record_id', disabled=True, metadata=True)],
        [sg.Text(text = "Name of User:"), sg.Input(key='name_user', disabled=True, metadata=True)],
        [sg.Text(text = "Material Category:"), sg.Combo(['Gels', 'Thermoplastic'], key ="material_category", disabled= True, enable_events=True, metadata=True)],
        [sg.Text(text = "Hydrogel Material Name:"), sg.Combo(['MA-GNP', 'GelMA', 'Alginate', 'Pluronic', 'dECM', 'Other'], key ="material_name", disabled = True, metadata=True)],
        [sg.Text(text = "Hydrophobic Material Name:"), sg.Combo(['PPF', 'PCL'], key ="material_name_2", disabled = True)],
        [sg.Text(text = "Solvent Type:"), sg.Combo(["PBS", "Milli-Q", "DMEM", "Organic Solvent", "No Solvent"], key ="solvent_type", disabled= True, metadata=True)],
        [sg.Text(text = "Material's Molecular Weight:"), sg.Input(key='mat_mw', disabled=True, do_not_clear=False)],
        [sg.Text(text = "Material's Molecular Weight (Unit):"), sg.Input(key='mat_mw_unit', disabled=True,  metadata=True)],
        [sg.Text(text = "Material's Viscosity:"), sg.Input(key='viscosity', disabled=True,  metadata=True)],
        [sg.Text(text = "Material's Viscosity (Units):"), sg.Input(key='viscosity_units', disabled=True,  metadata=True)],
        [sg.Text(text = "Material's Yield Strength:"), sg.Input(key='yield_strength', disabled=True,  metadata=True)],
        [sg.Text(text = "Material's Yield Strength (Units):"), sg.Input(key='yield_strength_unit', disabled=True,  metadata=True)],
        [sg.Text(text = "Gelation/Melting/Phase Change Temperature (C)"), sg.Input(key='gel_temp', disabled=True,  metadata=True)],
        [sg.Text(text = "The next two questions are asking for the shear thinning coefficients.\nFor more information about these parameters, please refer to attached paper.: shorturl.at/fkuNO", 
        key = "paxton", metadata='not_disable')],
        [sg.Text(text = "Shear Thinning Coefficient (K)"), sg.Input(key='stc_k', disabled=True,  metadata=True)],
        [sg.Text(text = "Shear Thinning Coefficient (n)"), sg.Input(key='stc_n', disabled=True,  metadata=True)],
        [sg.Text(text = "Solid/Polymer Concentration:"), sg.Input(key='polymer_concent', disabled=True,  metadata=True)],
        [sg.Text(text = "Solid/Polymer Content (Units):"), sg.Combo(["w/v %", "w/w %", "v/v %"], key ="content_units", disabled= True, metadata=True)],
        [sg.Text(text = "Additives:"), sg.Combo(["Yes", "No"], disabled= True, key = "additives", enable_events=True, metadata=True)],
        [sg.Text(text = "Addtivive Content:"), sg.Input(key='add_content', disabled=True,  metadata=True)],
        [sg.Text(text = "Addtivive Content (Units):"), sg.Combo(["w/v %", "w/w %", "v/v %"], key ="add_content_units", disabled= True, metadata=True)],
        [sg.Text(text = "Size of Additive (Diameter):"), sg.Input(key='add_diameter', disabled=True,  metadata=True)],
        [sg.Text(text = "Size of Additive (Diameter) (Units):"), sg.Input(key='add_diameter_unit', disabled=True,  metadata=True)],
        [sg.Text(text = "Printer Name:"), sg.Combo(["BioAssembly Bot", "Bioplotter", "CellLink", "Other"], key ="printer", disabled= True, metadata=True)]]

        layout =  [[sg.Column(col_new_trial), sg.Column(col_new_experiment)], 
        [sg.Button(button_text= "OK", enable_events= True, key ="OK")]]

        
        
        window = sg.Window('New Data', layout)

        

        # for elem in col_new_experiment:
        #     print(elem[0].Key)#we can key to get all the stuff in the column
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
                        if(elem.Key != None and elem.metadata != 'not_disable'):#do not block the radio button):
                            window[elem.Key].update(disabled = False)
                # print("I am here (new_exp_radio)")
                self.clear_disable_all(window, branch_log_dict, col_new_experiment)#we could just enable a few, instead
            elif event == "new_trial_radio":#if new trial is picked, diable the element fir the new experiment, enable for the new trua
                #disable everything in the form
                for row in col_new_experiment:
                    for elem in row:
                        if(elem.Key != None and elem.metadata != 'not_disable'):#do not block the radio button and do not update textboxes
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
                            if(elem.Key != None and elem.metadata != 'not_disable'):#do not check labels and the radio button
                                if (elem.metadata and values[elem.Key]== ""): #value ahs to be filled and not empty
                                    field_missing = True
                                    sg.popup_ok('Required fields are missing!')#if at least one field is empty, throw a popup and stop checking
                                    break  # Shows OK button
                                    #if at least one field does not have a value, then we generate a popup
                                elif(values[elem.Key] != ""):#add to the dictonary of paramaters
                                    printing_params[elem.Key] = values[elem.Key]
                        #all fields are filled
                        #we can return
                    if not field_missing:
                        # print("Here are printing_params in GUI_code.py:", printing_params)
                        #if user closes the popup, then the print is considered bad by default
                        print_result = "Good Print" if sg.popup_yes_no("Is it a good print?", title = "Print Quality") == "Yes" else "Bad Print"
                        window.close()
                        #now, we also return print_result
                        return "add_record", printing_params, print_result
                                                        
                elif values['new_trial_radio']:#could use else
                    # print("here are values of list_box", values['list'])
                    # print("here are values:", values)
                    if values['list'] == []:
                        sg.popup_ok('Required fields are missing!')
                        continue#go to while loop
                    #we got here, so we now the record_id of the experiment we want to do the new trial for
                    record_lst = api.get_elements(record_id=values['list'][0])
                    window.close()
                    return "add_trial", record_lst
            elif event in branch_log_dict:#if branching logic is dependent on this element
                #we could only enable/disable stuff affected by the element
                self.enable_selected(window, copy.deepcopy(values), branch_log_dict, event)
                self.disable_not_selected(window, copy.deepcopy(values), branch_log_dict, event)
            
            
            



import PySimpleGUI as sg
import requests
import API_calls
import re
import utils

#you could move this function to API calls
def get_experiment_names():
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
def get_elements(record_id):
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
def get_branching_logic():
    """
    Get the dictonary of branching logic
    """
    bran_dict = {}
    metadata = API_calls.get_metadata()
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
    


def start_GUI():
    """
    Does everything related to do the UI. Returns the type of the action to do and the other required parameter. In other words, 
    add a new trial or add a new experiment.
    
    """
    experiment_names = get_experiment_names()
    branch_log_dict = get_branching_logic()
    #Separate columns for a new trial and a new experiment
    col_new_trial = [[sg.Radio('New Trial', "RADIO1", default=True, enable_events = True, key="new_trial_radio")],
    [sg.Text(text = "Please pick your experiment from the list below:")], 
    [sg.Listbox(values=experiment_names, size=(30, 6), key="list", select_mode = sg.LISTBOX_SELECT_MODE_SINGLE)]]

    col_new_experiment = [[sg.Radio('New experiment', "RADIO1", enable_events=True, key="new_exp_radio")], 
    [sg.Text(text = "RecordID:"), sg.Input(key='record_id', disabled=True, do_not_clear=False)],
    [sg.Text(text = "Name of User:"), sg.Input(key='name_user', disabled=True, do_not_clear=False)],
    [sg.Text(text = "Material Category:"), sg.Combo(['Gels', 'Thermoplastic'], key ="material_category", disabled= True, enable_events=True)],
    [sg.Text(text = "Hydrogel Material Name:"), sg.Combo(['MA-GNP', 'GelMA', 'Alginate', 'Pluronic', 'dECM', 'Other'], key ="material_name", disabled = True)],
    [sg.Text(text = "Hydrophobic Material Name:"), sg.Combo(['PPF', 'PCL'], key ="material_name_2", disabled = True)],
    [sg.Text(text = "Solvent Type:"), sg.Combo(["PBS", "Milli-Q", "DMEM", "Organic Solvent", "No Solvent"], key ="solvent_type", disabled= True)],
    [sg.Text(text = "Material's Molecular Weight:"), sg.Input(key='mat_mw', disabled=True, do_not_clear=False)],
    [sg.Text(text = "Material's Molecular Weight (Unit):"), sg.Input(key='mat_mw_unit', disabled=True, do_not_clear=False)],
    [sg.Text(text = "Material's Viscosity:"), sg.Input(key='viscosity', disabled=True, do_not_clear=False)],
    [sg.Text(text = "Material's Viscosity (Units):"), sg.Input(key='viscosity_units', disabled=True, do_not_clear=False)],
    [sg.Text(text = "Material's Yiel Strength:"), sg.Input(key='yield_strength', disabled=True, do_not_clear=False)],
    [sg.Text(text = "Material's Yiel Strength (Units):"), sg.Input(key='yield_strength_unit', disabled=True, do_not_clear=False)],
    [sg.Text(text = "Gelation/Melting/Phase Change Temperature (C)"), sg.Input(key='gel_temp', disabled=True, do_not_clear=False)],
    [sg.Text(text = "The next two questions are asking for the shear thinning coefficients.\n\
    For more information about these parameters, please refer to attached paper.:"), sg.Input(key='paxton', disabled=True, do_not_clear=False)],
    [sg.Text(text = "Shear Thinning Coefficient (K)"), sg.Input(key='stc_k', disabled=True, do_not_clear=False)],
    [sg.Text(text = "Shear Thinning Coefficient (n)"), sg.Input(key='stc_n', disabled=True, do_not_clear=False)],
    [sg.Text(text = "Solid/Polymer Concentration:"), sg.Input(key='polymer_concent', disabled=True, do_not_clear=False)],
    [sg.Text(text = "Solid/Polymer Content (Units):"), sg.Combo(["w/v %", "w/w %", "v/v %"], key ="content_units", disabled= True)],
    [sg.Text(text = "Additives:"), sg.Combo(["Yes", "No"], disabled= True, key = "additives")],
    [sg.Text(text = "Printer Name:"), sg.Combo(["BioAssembly Bot", "Bioplotter", "CellLink", "Other"], key ="printer", disabled= True)]]
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
            return None, None
        elif event == "new_exp_radio":#if new experiment is picked, then disable the elements for the new trial
            window['list'].update(disabled = True)
            for row in col_new_experiment:
                for elem in row:
                    if(elem.Key != None and elem.Key != "new_trial_radio"):#do not block the radio button):
                        window[elem.Key].update(disabled = False)
        elif event == "new_trial_radio":#if new trial is picked, diable the element fir the new experiment, enable for the new trua
            #disable everything in the form
            for row in col_new_experiment:
                for elem in row:
                    if(elem.Key != None and elem.Key != "new_exp_radio"):#do not block the radio button and do not update textboxes
                        window[elem.Key].update(disabled = True)
            #enable the listbox
        
            window['list'].update(disabled = False)
        elif event == "OK":
            field_missing = False
            #Check if the listbox has a value or the form has a value
            if values['new_exp_radio']:#we are doing new expriment
                printing_params = {}
                #Check the all the stuff in the form of the new experiment
                for row in col_new_experiment:
                    if(field_missing):
                        break#do not check anymore
                    for elem in row:
                        if(elem.Key != None and elem.Key != "new_exp_radio"):#do not check labels and the radio button
                            if values[elem.Key]== "": #make sure the values are not disabled
                                field_missing = True
                                sg.popup_ok('Required fields are missing!')#if at least one field is empty, throw a popup and stop checking
                                break  # Shows OK button
                                #if at least one field does not have a value, then we generate a popup
                            else:#add to the dictonary of paramaters
                                printing_params[elem.Key] = values[elem.Key]
                    #all fields are filled
                    #we can return
                if not field_missing:
                    print("Here are printing_params in GUI_code.py:", printing_params)
                    window.close()
                    return "add_record", printing_params
                                                    
            elif values['new_trial_radio']:#could use else
                print("here are values of list_box", values['list'])
                print("here are values:", values)
                if values['list'] == []:
                    sg.popup_ok('Required fields are missing!')
                    continue#go to while loop
                #we got here, so we now the record_id of the experiment we want to do the new trial for
                record_lst = get_elements(record_id=values['list'][0])
                window.close()
                return "add_trial", record_lst
            #add branching logic(7/5/2021)
        elif event in branch_log_dict:#if branching logic is dependent on this event
            print("You triggered a bran logic UI element")
            #transfrom into numerical args
            record = {event:values[event]}
            utils.convert_to_numeric(record)#record is modified
            for gui_element in branch_log_dict[event][record[event]]:
                window[gui_element].update(disabled = False)#enable the once that require the value record[event]
            #disable others
            for value in branch_log_dict[event]:
                if(value != record[event]):#disable all else
                    for gui_element in branch_log_dict[event][value]:
                        window[gui_element].update(disabled = True)
        else:
            print(event)


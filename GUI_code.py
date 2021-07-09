import PySimpleGUI as sg
import requests

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

def start_GUI():
    """
    Does everything related to do the UI. Returns the type of the action to do and the other required parameter. In other words, 
    add a new trial or add a new experiment.
    
    """
    experiment_names = get_experiment_names()
    #Separate columns for a new trial and a new experiment
    col_new_trial = [[sg.Radio('New Trial', "RADIO1", default=True, enable_events = True, key="new_trial_radio")],
    [sg.Text(text = "Please pick your experiment from the list below:")], 
    [sg.Listbox(values=experiment_names, size=(30, 6), key="list", select_mode = sg.LISTBOX_SELECT_MODE_SINGLE)]]

    col_new_experiment = [[sg.Radio('New experiment', "RADIO1", enable_events=True, key="new_exp_radio")], 
    [sg.Text(text = "RecordID:"), sg.Input(key='record_id', disabled=True, do_not_clear=False)],
    [sg.Text(text = "Name of User:"), sg.Input(key='name_user', disabled=True, do_not_clear=False)],
    [sg.Text(text = "Material Category:"), sg.Combo(['Gels', 'Thermoplastic'], key ="material_category", disabled= True)],
    #[sg.Text(text = "Hydrogel Material Name:"), sg.Combo(['MA-GNP', 'GelMA', 'Alginate', 'Pluronic', 'dECM', 'Other'], key ="material_name", disabled = True)],
    [sg.Text(text = "Hydrophobic Material Name:"), sg.Combo(['PPF', 'PCL'], key ="material_name_2", disabled = True)],
    [sg.Text(text = "Solvent Type:"), sg.Combo(["PBS", "Milli-Q", "DMEM", "Organic Solvent", "No Solvent"], key ="solvent_type", disabled= True)],
    [sg.Text(text = "Material's Molecular Weight:"), sg.Input(key='mat_mw', disabled=True, do_not_clear=False)],
    [sg.Text(text = "Material's Molecular Weight (Unit):"), sg.Input(key='mat_mw_unit', disabled=True, do_not_clear=False)],
    [sg.Text(text = "Solid/Polymer Concentration:"), sg.Input(key='polymer_concent', disabled=True, do_not_clear=False)],
    [sg.Text(text = "Solid/Polymer Content (Units):"), sg.Combo(["w/v %", "w/w %", "v/v %"], key ="content_units", disabled= True)],
    [sg.Text(text = "Additives:"), sg.Combo(["Yes", "No"], disabled= True, key = "additives")],
    [sg.Text(text = "Printer Name:"), sg.Combo(["BioAssembly Bot", "Bioplotter", "CellLink", "Other"], key ="printer", disabled= True)]]
    layout =  [[sg.Column(col_new_trial), sg.Column(col_new_experiment)], 
    [sg.Button(button_text= "OK", enable_events= True, key ="OK")]]

    #Make a dictonary of the format{field: {value: [list of fields that can be filled when the value is picked]}}
    window = sg.Window('New Data', layout)

    # for elem in col_new_experiment:
    #     print(elem[0].Key)#we can key to get all the stuff in the column
    while True:
        event, values = window.read()
        # End program if user closes window or
        # presses the OK button
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
        #add branching logic(7/5/2021)
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
                        if(elem.Key != None and elem.Key != "new_exp_radio"):#do check labels and the radio butto
                            if values[elem.Key]== "":
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
            # else:#event is triggered by the by one fields  
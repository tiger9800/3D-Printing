import GUI_code
import populate_db
import prepare_params
import read_on_create


lines = []
read_on_create.start_watching(lines)
params = prepare_params.parse_export(lines)
redcap_params = prepare_params.XML_to_REDCap(params)
params_converted = prepare_params.params_clean_convert(redcap_params)
#Now, we need to start the GUI code
func_name, record_trial_info = GUI_code.start_GUI()
if func_name == "add_record":
    populate_db.add_record(record_trial_info, params_converted)
if func_name == "add_trial":
    populate_db.add_trial(record_trial_info, params_converted)
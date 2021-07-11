import pandas as pd #for working with the CSV mapping
import numpy as np

# it is not ideal to have this here, maybe better insinde XML_to_REDCap ?
# this csv file can also be a parameter of the main
name_mapping = pd.read_csv("Programming to XML to REDCap.csv")


def parse_export(lines):
    """
    Parse the .bpm file.
    
    """
    params = {}
    for line in lines:
        if(line[:2] != "</") and ('</' in line): #if not only closing tag
            key = line[line.index('<')+1:line.index('>')]
            value = line[line.index(">") + 1:line.index('</')]
            params[key] = value
    return params

def XML_to_REDCap(params):
    """
    Convert the paramters from the XML into REDCap naming format. Also,
    only keep the paramters from the XML that are present in the REDCap database.
    
    params - dict of XML paramaters. 
    """
    params_new = {}
    for XML_param in params:
        new_key = name_mapping[name_mapping['XML']==XML_param]['REDCap (field_name)'].iloc[0]
        if (not pd.isnull(new_key)):#check if there is a corresponding value in the REDCap (field_name)
            params_new[new_key] = params[XML_param]
    return params_new

#this function could also use some refactoring - we can discuss later
def params_clean_convert(params_new):
    """
    Converts the parameters extracted from the .bpm export file to the appropriate units.
    
    params_converted are the parameters ready to be inputted into the database. 
    """
    conversion_dict = {("mm", "microm"):1000, ("ms", "s"):1/1000}
    #if the units not the same, then use proper conversion
    params_converted = {}
    for param in params_new:
        if(param != "needle_size"):
            params_converted[param] = float(params_new[param])
        else:
            params_converted[param] = params_new[param]
            continue
        r_units = name_mapping[name_mapping['REDCap (field_name)']==param]['REDCap Units'].iloc[0]
        xml_units = name_mapping[name_mapping['REDCap (field_name)']==param]['XML Units'].iloc[0]
        if not(r_units == xml_units):
             params_converted[param] = params_converted[param]*conversion_dict[(xml_units, r_units)]
            #We need to convert and for that, we need a dictonary
    #Get just one post flow
    #hmm this is also unclear to me, but ok
    params_converted['post_flow'] += -params_converted['-post_flow']
    del params_converted['-post_flow']
    return params_converted

def get_final_params(lines):
    params = parse_export(lines)
    redcap_params = XML_to_REDCap(params)
    params_converted = params_clean_convert(redcap_params)
    return params_converted

# 3D-Printing

This is a program currently compatible with Visual Machines software  
for EnvisionTec Bioplotter. It parses printing paramaters given to the printer.  
Also it collects and validates material infomation from a user through a GUI.  
After it validates the data, it intiates an import into a REDCap database.  


# Instructions for running  
  
Create a .txt file in the same directory as the program files called token.txt.  
Add a JSON-formatted name-token pairs (ex.(not an actual token value) {"Davyd":"23435545"}),  
where token corresponds to your REDCap project API.  
In the directory where the program files are locted run:  
python ./main.py [<name>(one of the specified in the token.txt)] [-loc(location of the .zip file produced by Visual Machines)]  
  
The program, will monitor the creation of .zip files in loc and start the GUI upon creation.  
  
GUI_code.py - contains the code for the GUI, including validation of the info  
inputted by the user.  
prepare_params.py - contains all the routines used for parsing the file  
produced by Visual Machines Software  
api_calls.py - contains the methods for importing the data into a REDCap project.  
  
4) provide documentation  

for automated documentation generators check this out:  

https://towardsdatascience.com/auto-docs-for-python-b545ce372e2d


""" XML files modification """

import os
import string as str

folder_path = "/Users/llemcf/Desktop/ETH_stage_2022/6_Mylene_work_graphs_digitization/Test"

folders = os.listdir(folder_path) 
for folder in folders :
    if folder != ".DS_Store" :
        files_path = folder_path + "/" + folder
        files = os.listdir(files_path) 
        for file in files : 
            if "xml" in file : 
                name_file = files_path + "/" + file
                
                # open the file to get the xml data
                inFile = open(name_file, "r")  
                data = inFile.readlines()
                inFile.close()

                # write the xml data to the file 
                outFile = open(name_file, 'w')
                data[3] = data[3].replace("null","data.png")
                outFile.writelines(data)
                outFile.close()
    














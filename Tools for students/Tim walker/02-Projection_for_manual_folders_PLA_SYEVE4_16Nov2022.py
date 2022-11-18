############################################################################################################################################################
'''

Full name of script: Image projection and background subtraction for manually acquired folders of PLA experiment in EV and E4 TMEM127 KO SH-SY5Y cells  [V 01]

Script languague: Jython (Python wrapper for Java, run with ImageJ/Fiji app -not pyImageJ-)

Description: This script is reused code from the PART 4 of https://github.com/EdRey05/Tools for students/Tim Walker/01-Image_Processing_PLA_SYEVE4_16Nov2022.py
			 and was made because there were few and sparse cells in some of the channels in the channel slide, so automated imaging and stitching was not 
			 possible. Those images were instead merged into hyperstacks using the general script (Tools for EVOS-M7000 images/Images_to_Hyperstacks_merger.py) 
			 and then this script was run to make the Z-projection and background subtraction required for further steps.

Made by: Eduardo Reyes Alvarez

Contact: eduardo_reyes09@hotmail.com

Last update: November 18, 2022

Version History:
V01 (November 18, 2022): First version of the script adapted as a standalone part (it required minor edits from the original script, mostly name of a missing
						 variable and change variable names to refer to "merged" images instead of "stitched").

'''

############################################################################################################################################################
############################################################################################################################################################
########################################## Import neccesary packages and make the interactive menu #########################################################

import os
import time
from datetime import datetime
from ij import IJ, ImagePlus
from ij import WindowManager

#@ File    (label = "Experiment folder", style = "directory") experiment_directory
#@ String (visibility=MESSAGE, value="Script made by: Eduardo Reyes-Alvarez", required=false) msg6

#Get full path of raw images and the cells folder from the menu
experiment_directory = experiment_directory.getAbsolutePath()

############################################################################################################################################################
################################################## PART 4 - MAKE PROJECTION AND SUBTRACT BACKGROUND ########################################################

######################################################### Make Z-projection for data analysis ##############################################################

#Start the timer
starting_time = datetime.now()

#Find the folder with the merged images to use
merging_saving_path = os.path.join(experiment_directory, "Raw Images_Merged")

#Make folder to save the processed images
projections_saving_path = os.path.join(experiment_directory, "Processed Images for Analysis")
if not os.path.exists(projections_saving_path):
	os.makedirs(projections_saving_path)

#Scan the folder were all the merged images are
for folder, subfolder, merged_images in os.walk(merging_saving_path):
    
    #Iterate through the merged images
    for merged_image in merged_images:
    	
        #Open a merged image 
        original_image = IJ.openImage(os.path.join(folder, merged_image))
        while original_image==None:
            time.sleep(1)
        original_image.show()
        
        #Make the Z-projection
        IJ.run("Z Project...", "projection=[Max Intensity]")
        
        #Close the original -heavier- image and clear some memory
        original_image.close()
        time.sleep(1)
        IJ.run("Collect Garbage", "")
        time.sleep(1)
        IJ.run("Collect Garbage", "")
        
        #Subtract the background to clean the image and improve contrast
        projected_image = IJ.getImage()
        IJ.run("Subtract Background...", "rolling=150")
        projected_image = IJ.getImage()
        
        #Save the projection
        projections_saving_name = os.path.join(projections_saving_path, projected_image.getTitle())
        IJ.saveAs(projected_image, "Tiff", projections_saving_name)
        time.sleep(2)
        
        #Close the image and clear the memory
        projected_image.close()
        time.sleep(1)
        IJ.run("Collect Garbage", "")
        time.sleep(1)
        IJ.run("Collect Garbage", "")
        
        #Print the status of the process
        print("Image processed: ", merged_image)

################################################################### End of the processing ##################################################################

#Finish the timer and get the total number of seconds spent
ending_time = datetime.now()
processing_time = (ending_time.getTime() - starting_time.getTime())/1000.00

#Print a summary of the work done and time it required
print("Processing time (min):", round(processing_time/60, 1))

############################################################################################################################################################

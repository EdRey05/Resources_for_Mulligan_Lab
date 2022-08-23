######################################################################################################################################################################
'''

Full name of script: Tool 03 to save ROIs for Proximity Ligation Assay (PLA) quantification  [Version 01]

Script languague: Jython (Python wrapper for Java, run with ImageJ/Fiji app -not pyImageJ-)

Description: This is a short script that helps an user openning the two sets of ROIs (For Presentation and For Analysis) for an image, made before or by somebody else
             with the purpose to review the image to add more cells that look good for analysis and were not included before. This script asks to select an image from
			 the raw or processed folder, which should be open and in the same folder as another called "ROIs". The latter must contain 2 folders: "For Presentation" 
			 which contains the ROIs for data presentation, and "For Analysis" which contains the areas quantified. The script finds the subfolder with the name of the
			 image selected inside these 2 folders of ROIs and iterates through them, opening first the "X_1.roi" and then "X_2.roi". Finally, once the user loads the 
			 current ROIs, they can proceed to draw more in the same order (rectangle first, polygon second) and use the script called "Tool 01 to save ROIs for PLA 
			 quantification" to save all of them. Note: if the nimages have a name in a different format than "MAX_Row_01_05.tif", edit the lines that crop the image
			 selected to find the its folders.

Made by: Eduardo Reyes Alvarez

Contact: eduardo_reyes09@hotmail.com

Last update: Aug 23, 2022

Version History:
V01 (Aug 23, 2022): First working version, fully annotated. 

'''
######################################################################################################################################################################
################################################### Import neccesary packages and make the interactive menu ##########################################################

import os
import time
from datetime import datetime
from ij import IJ, ImagePlus
from ij import WindowManager
from ij.plugin.frame import RoiManager
from ij.gui import Roi


IJ.run("Collect Garbage", "")

#@ String (visibility=MESSAGE, value="", required=false) msg1
#@ File    (label = "Select an image", style = "file") image_processed

#Full path of the image (inside channel or condition folder / Processed Images for Analysis / ) 
image_processed_directory = image_processed.getAbsolutePath()

################################################## Prepare the directories and iterate through them, opening the ROIs ################################################

#The images have a name "MAX_Row_01_05.tif" so we need to remove the extension and the left side
image_name = os.path.split(os.path.splitext(image_processed_directory)[0])[1]
image_name = image_name.split("X_")[1]

#Prepare the directories for the ROIs
ROIs_folder = os.path.join(os.path.split(os.path.split(image_processed_directory)[0])[0], "ROIs")
presentation_ROIs_folder = os.path.join(ROIs_folder, "For Presentation", image_name)
analysis_ROIs_folder = os.path.join(ROIs_folder, "For Analysis", image_name)

#Initialize the ROI manager
rm = RoiManager()

#Iterate for all the ROIs fond in the "For Presentation" folder
for ROI_folder, subfolder, ROIs in os.walk(presentation_ROIs_folder):
	
	for ROI in ROIs:
		
		#Open each ROI found in the For Presentation folder
		rm.runCommand("Open", os.path.join(ROI_folder, ROI))
		
		#Open each ROI with the same name but in the For Analysis Folder
		rm.runCommand("Open", os.path.join(ROI_folder, ROI).replace("Presentation", "Analysis").replace("_2", "_1"))

#Let the user know the script is done
print("\n \t All the ROIs have been opened!")


######################################################################################################################################################################
######################################################################################################################################################################
######################################################################################################################################################################
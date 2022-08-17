#######################################################################################################################################################################
#######################################################################################################################################################################
#######################################################################################################################################################################
'''

Full name of script: Tool 01 to save ROIs for Proximity Ligation Assay (PLA) quantification  [Version 01]

Script languague: Jython (Python wrapper for Java, run with ImageJ/Fiji app -not pyImageJ-)

Description: This is a short script that helps the user saving and separating the ROIs drawn on an image, as well as making a jpg preview with the selected ROIs for
             presentation (rectangular ones). These are saved to  a temporary folder selected by the user, which need to be moved before proceeding to other images.
             Once an image is opened, the user must select in the ROI manager "Properties", then border thickness = 11 and colour white, click OK, then select in the
             manager "More" -> "Labels", select the label size of ~18 and click OK. Before running the script, draw a rectangular ROI for a cell (which will be used
             for result preview or presentation in a ppt), add it to the ROI manager, then draw an ROI with the polygon tool to go around the edges of the cell (the 
             puncta inside this delimited ROI will be quantified), add it to the manager, and do so for all the cells of interest in the image. The ROI manager starts
             counting at 0, so the script saves all the even-numbered ROIs (0, 2, 4...) with a name "X_2.roi" in the folder "For Presentation", and all the 
             odd-numbered ROIs (1, 3, 5...) with a name "X_1.roi" in the folder "For Analysis". The script first loops over all the ROIs drawn, renames them, saves 
             them, and then loops in reverse order to close all the "X_1.roi" odd numbers to generate a .jpg image with the rectangles flattened on the image to 
             highlight the cells selected with the label (doing this with the ROIs around the edge of the cell doesn't allow for good visualization of the cells 
             selected).  Following those steps it is recommended to make sure all the cells have two sets of ROIs and in the right order. Run the script and once done,
             verify the preview image has only rectangles (otherwise start over), delete all the ROIs left in the manager, move the files from the temporary folder to
             the corresponding one, close all the images, open the next one and repeat the process.

Made by: Eduardo Reyes Alvarez

Contact: eduardo_reyes09@hotmail.com

Last update: Aug 05, 2021

Version History:
V01 (Aug 05, 2021): First working version, fully annotated. For simplicity, the two sets of ROIs are saved to a temporary folder, and the user needs to move the files
                    to the corresponding directory before continuing with the next image.

'''

#######################################################################################################################################################################
########################################## Import neccesary packages and make the interactive menu ####################################################################

import os
import time
from datetime import datetime
from ij import IJ, ImagePlus
from ij import WindowManager
from ij.plugin.frame import RoiManager
from ij.gui import Roi

#In case the memory from the previous image hasnt been cleared
IJ.run("Collect Garbage", "")

#Ask user for a temporary folder to put the ROIs and preview images on
#@ File    (label = "Save ROIs to folder...", style = "directory") ROI_temp_directory
ROI_temp_directory = ROI_temp_directory.getAbsolutePath()

#Make the subfolders for each set of ROIs
ROIs_for_analysis_folder = os.path.join(ROI_temp_directory, "For Analysis")
if not os.path.exists(ROIs_for_analysis_folder):
						os.makedirs(ROIs_for_analysis_folder)
ROIs_for_presentation_folder = os.path.join(ROI_temp_directory, "For Presentation")
if not os.path.exists(ROIs_for_presentation_folder):
						os.makedirs(ROIs_for_presentation_folder)

#Start the ROI manager (in a variable), get the content of the current manager window, and count the ROIs drawn
rm = RoiManager()
rm = rm.getRoiManager()
total_ROIs = rm.count

#Iterate through all the ROIs
for ROI_index in range(total_ROIs):
	
	#Select the ROIs, one by one
	rm.select(ROI_index)
	
	#Decide how to rename it and where according to its index number (evens = _2 For Presentation, odds = _1 For Analysis)
	if ROI_index % 2 == 0:
		label_number = (ROI_index/2) + 1
		label_text = str(label_number)+"_2"
		rm.runCommand("Rename", label_text)
		saveROI_tofolder = ROIs_for_presentation_folder
	else:
		label_number = int((ROI_index+1)/2)
		label_text = str(label_number)+"_1"
		rm.runCommand("Rename",label_text)
		saveROI_tofolder = ROIs_for_analysis_folder
	
	#Save the current ROI once it is renamed
	rm.save(os.path.join(saveROI_tofolder, label_text+".roi"))

#Iterate backwards (not sure if removing the first ROIs shifts all the other indices, it shouldn't in python but probably in ImageJ, so safer to go backwards)
for ROI_index in reversed(range(total_ROIs)):
	
	#Do nothing for even numbers, select and delete all the odd-numbered ROIs
	if ROI_index % 2 != 0:
		rm.select(ROI_index)
		rm.runCommand("Delete")

#Get the current image and its name to generate a preview with the selected ROIs
current_image = IJ.getImage()
current_image_name = current_image.getTitle()
current_image_name = current_image_name.split(".")[0]
current_image_name = current_image_name.split("X_")[1]

#Select all the ROIs still in the manager and show the labels
rm.runCommand(current_image,"Show All with labels")
rm.setGroup(0)
rm.setPosition(0)
rm.runCommand("Set Color", "white")
rm.runCommand("UseNames", "true")

#Flatten the image and save it as .jpg
IJ.run("Flatten")
flattened_image = IJ.getImage()
IJ.saveAs(flattened_image, "Jpeg", os.path.join(ROI_temp_directory, "ROIs_selected_"+current_image_name+".jpg"))

#######################################################################################################################################################################
#######################################################################################################################################################################
#######################################################################################################################################################################

######################################################################################################################################################################
'''

Full name of script: Tool 02 to save ROIs for Proximity Ligation Assay (PLA) quantification  [Version 01]

Script languague: Jython (Python wrapper for Java, run with ImageJ/Fiji app -not pyImageJ-)

Description: This is a short script that helps two users saving ROIs for PLA results presentation and quantification. Once an image is opened, the user must select 
             in the ROI manager "Properties", then border thickness/width = 11 and colour white, click OK, then select in the ROI manager "More" -> "Labels", select 
             the label size of ~18 and click OK. Before running the script, both users need to draw the ROI for all the cells of interest, add them to the ROI manager,
             de-select Show all and de-select the last ROI drawn. Now, the user who picked the good cells and made the rectangular ROIs can run the script as it is,
             and select the image opened clicking in the top Browse button (ignore the duplicated second button, alternatively, you can just delete from the scrit the
             lines 92 to 148 to avoid confusion, that would remove the duplication). After a few seconds, all the ROIs are labeled, and saved in the root location of
             the image selected (assuming structure: Condition/root -> Processed Images -> Row_X_Y_.tif), under the folder ROIs->For Presentation. It will also make
             and save the flattened image, so you can close everything and delete the ROIs before proceeding to the next image. The person drawing the second set of 
             ROIs also has a similar folder structure, they will work with the jpg flattened images and drawing polygonal ROIs on that image, then delete the lines
             31 to 92 and remove the quotation marks on lines 97 and 150. After that you can run the script, select the image and the script will save all the ROIs.
             Finally, delete all the ROIs, close the current image and open the next one and repeat.

Made by: Eduardo Reyes Alvarez

Contact: eduardo_reyes09@hotmail.com

Last update: Aug 08, 2022

Version History:
V01 (Aug 08, 2022): First working version, fully annotated. This script includes two parts that should be separated into 2 scripts for a person selecting cells and
                    drawing rectangular ROIs, and another person helping with the polygonal ROIs.

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
#@ File    (label = "Select the image completed", style = "file") image_processed

#Full path of the image (inside channel or condition folder / Processed Images for Analysis / ) 
image_processed_directory = image_processed.getAbsolutePath()

#Prepare the directories for the ROIs
ROIs_folder = os.path.split(image_processed_directory)[0]
ROIs_folder = ROIs_folder.replace("Processed Images for Analysis", "ROIs")
presentation_ROIs_folder = os.path.join(ROIs_folder, "For Presentation")

#From the image directory, remove the extension first, then split to remove the whole path on the left and keep just the name
image_name = os.path.split(os.path.splitext(image_processed_directory)[0])[1]
image_name = image_name.split("X_")[1]

#Prepare directory for specific image under the ROIs for Presentation folder, where the current ROIs will be saved
saveROI_tofolder = os.path.join(presentation_ROIs_folder, image_name)

#Initialize the ROI manager, get all the ROIs drawn and count them
rm = RoiManager()
rm = rm.getRoiManager()
total_ROIs = rm.count

#Iterate for all the ROIs currently in the manager
for ROI in range(total_ROIs):
	
	#Select the ROIs one by one, re-label in this format "10_2" and save
	rm.select(ROI)
	label_ROI_as = str(ROI)+"_2"
	rm.runCommand("Rename", label_ROI_as)
	rm.save(os.path.join(saveROI_tofolder, label_ROI_as+".roi"))

#Prepare and save the jpeg preview of the selected ROIs
current_image = IJ.getImage()
rm.runCommand(current_image,"Show All with labels")
rm.setGroup(0)
rm.setPosition(0)
rm.runCommand("Set Color", "white")
rm.runCommand("UseNames", "true")
IJ.run("Flatten")
flattened_image = IJ.getImage()
IJ.saveAs(flattened_image, "Jpeg", os.path.join(ROIs_folder, "ROIs_selected_"+image_name+".jpg"))

#Close the original image, and review the result
current_image.close()
print("\n \t All the ROIs have been saved!")


######################################################################################################################################################################
######################################################################################################################################################################
######################################################################################################################################################################

'''
#Section for the 2nd part (for people helping doing the polygon ROIs for analysis)
#For the person doing the first part (selecting cells and doing rectangular ROIs for presentation): you can leave the code below here, just select the image
#in the first "Browse" button when you run the script, the second is just duplicated from the code below but doesnt do anything (or delete everything below line 100).
#For the person doing the second part (polygon ROIs for puncta quantification): you need to delete the code above (line 31 to 92) and then remove the 
# 3 quotation signs on lines 97 and 150 before running the script.

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
#@ File    (label = "Select the image completed", style = "file") image_processed

#Full path of the image (inside channel or condition folder / Processed Images for Analysis / ) 
image_processed_directory = image_processed.getAbsolutePath()

#Prepare the directories for the ROIs
ROIs_folder = os.path.split(image_processed_directory)[0]
analysis_ROIs_folder = os.path.join(ROIs_folder, "For Analysis")

#From the image directory, remove the extension first, then split to remove the whole path on the left and keep just the name
image_name = os.path.split(os.path.splitext(image_processed_directory)[0])[1]
image_name = image_name.split("selected_")[1]

#Prepare directory for specific image under the ROIs for Presentation folder, where the current ROIs will be saved
saveROI_tofolder = os.path.join(analysis_ROIs_folder, image_name)

#Initialize the ROI manager, get all the ROIs drawn and count them
rm = RoiManager()
rm = rm.getRoiManager()
total_ROIs = rm.count

#Iterate for all the ROIs currently in the manager
for ROI in range(total_ROIs):
	
	#Select the ROIs one by one, re-label in this format "10_1" and save
	rm.select(ROI)
	label_ROI_as = str(ROI)+"_1"
	rm.runCommand("Rename", label_ROI_as)
	rm.save(os.path.join(saveROI_tofolder, label_ROI_as+".roi"))

#Inform the user saving has finished
print("\n \t All the ROIs have been saved!")

'''

######################################################################################################################################################################
######################################################################################################################################################################

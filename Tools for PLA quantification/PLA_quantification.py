###################################################################################################################################################################
###################################################################################################################################################################
###################################################################################################################################################################
'''

Full name of script: Proximity Ligation Assay (PLA) quantification  [Version 02]

Script languague: Jython (Python wrapper for Java, run with ImageJ/Fiji app -not pyImageJ-)

Description: This script scans through a "raw images" folder to find images that can be opened in ImageJ/Fiji (.tif, .czi, etc) and uses the folder/directory 
             structure where those images are to find 2 sets of regions of interest (ROIs). The user has to input through the interactive menu that directory
             as well as two more, ideally in the same location as the raw images folder: an "Analysis" folder that needs to contain a subfolder "ROIs_analyzed"
             with the ROIs to quantify the PLA puncta on, and a "Cropped_cells" folder that needs to contain a sulfolder "ROIs_used_to_crop" if the user wants
             to generate cropped images of the cells analyzed for quick visual inspection or data presentation on a power point presentation. The script does 3
             things: crops cells (optional), isolates + thresholds (user has to select a method) + saves the PLA channels, and finally, quantifies the puncta of
             the thresholded images using the appropriate set of ROIs. The output files are given under "Analysis/Output_files/" and are "Measures.csv" which
             corresponds to the areas of each cell quantified (in case puncta per cell needs to be normalized by cell area) and "Particles.csv" which contains 
             the number of puncta/particles of each cell. The script iterates through any given number of cells in the raw images folder as long as it can find
             the same folder+subfolder structure in the ROIs folders.

Made by: Eduardo Reyes Alvarez

Contact: eduardo_reyes09@hotmail.com

Last update: June 20, 2021

Version History:
V01 (Jun 01, 2021): First working version of the script. Requires a specific folder structure and 2 sets of ROIs per cell of interest. Some outputs are optional
                    such as cropped images of each cell, each PLA channel thresholded and the actual quantification (excel files). Code fully annotated.
V02 (June 20, 2021): Fixed/improved some directory handling during the iterations. Some steps can be improved: data saving and iteration through the images + 
                     ROIs when the raw images are heavy.
'''

###################################################################################################################################################################
########################################## Import neccesary packages and make the interactive menu ################################################################

import os
import time
from datetime import datetime
from ij import IJ, ImagePlus
from ij import WindowManager
from ij.plugin.frame import RoiManager
from ij.gui import Roi

#@ File    (label = "Raw Images folder", style = "directory") raw_image_directory
#@ Integer  (label = "PLA channel number", style = "slider", min=1, max=5, stepSize=1) PLA_channel
#@ String   (label = "Threshold method", style = "listBox", choices = { "Default", "Huang", "Intermodes","IsoData", "IJ_IsoData", "Li", "MaxEntropy", "Mean", "MinError", "Minimum", "Moments", "Otsu", "Percentile", "RenyiEntropy", "Shanbhag", "Triangle", "Yen"}) threshold_method
#@ File    (label = "Cropped cells folder", style = "directory") cells_directory
#@ File    (label = "Analysis folder", style = "directory") analysis_directory
#@ Boolean   (label="Crop cells", style = "checkbox") Crop_cells
#@ Boolean   (label="PLA thresholding", style = "checkbox") PLA_thresholding
#@ Boolean   (label="Quantification", style = "checkbox") Quantification
#@ String (visibility=MESSAGE, value="Script made by: Eduardo Reyes-Alvarez", required=false) msg3

#Start the timer
starting_time = datetime.now()

#Get full path of raw images and the cells folder from the menu
raw_image_directory = raw_image_directory.getAbsolutePath()
analysis_directory = analysis_directory.getAbsolutePath()

###################################################################################################################################################################
######################################### Crop all the individual cells from raw images (Optional) ################################################################

#If the raw cells are big images with lots of cells, this will be done for data/results presentation, if not, then proceed to the next section
if Crop_cells==True:
	cropped_cells_directory = cells_directory.getAbsolutePath()
	ROIs_cropped_cells_directory = os.path.join(cropped_cells_directory, "ROIs_used_to_crop")
	
	#Walk through the raw image folder in case files or subfolders are used
	for raw_temp_directory, subfolder, raw_image_names in os.walk(raw_image_directory):
		raw_image_names.sort()

		#Iterate through each raw image 
		for raw_image_name in raw_image_names:

			#If Croppig cells, there MUST be a subfolder called ROIs_used_to_crop in the folder Cells with the same directory structure as the Raw_images
			ROIs_to_crop_folder = os.path.join(raw_temp_directory.replace(raw_image_directory, ROIs_cropped_cells_directory), os.path.splitext(raw_image_name)[0])
			
			#Walk through the ROIs folder, in case files or subfolders are used
			for ROI_temp_directory, subfolder2, ROIs in os.walk(ROIs_to_crop_folder):
				
				#Iterate through each ROI (of each raw image)
				for ROI in ROIs:
					
					#Open the current raw image
					current_raw_image = IJ.openImage(os.path.join(raw_temp_directory, raw_image_name))
					current_raw_image.show()
					image_opened = WindowManager.getWindow(raw_image_name)

					#If the image is big and heavy, ImageJ will take a moment to open it, so we delay the script to wait for it
					while image_opened==None:
						time.sleep(0.5)

					#Load the ROI manager and open the current ROI
					rm = RoiManager()
					current_ROI_directory = os.path.join(ROI_temp_directory, ROI)
					rm.runCommand("Open", str(current_ROI_directory))
					rm.select(0)
					
					#Crop the raw image with the current ROI and save it
					IJ.run("Crop")
					IJ.selectWindow(1)
					cropped_cell = IJ.getImage()

					#Make the directories and names to save the images
					save_cropped_directory = ROI_temp_directory.replace(ROIs_cropped_cells_directory, cropped_cells_directory)
					save_cropped_name = os.path.join(save_cropped_directory, os.path.splitext(ROI)[0])					
					if not os.path.exists(save_cropped_directory):
						os.makedirs(save_cropped_directory)

					#Save cropped image, give it 2 seconds to finish, close everything and flush the memory
					IJ.saveAs(cropped_cell, "Tiff", save_cropped_name)
					print("Cropped cell:", ROI)
					time.sleep(2)
					IJ.run("Close All")
					rm.close()
					IJ.run("Collect Garbage", "")

###################################################################################################################################################################
################################################################### PLA channel thresholding ######################################################################

if PLA_thresholding==True:

	#Walk through the raw image folder in case files or subfolders are used
	for raw_temp_directory, subfolder, raw_image_names in os.walk(raw_image_directory):
		raw_image_names.sort()
	
		#Iterate through each raw image 
		for raw_image_name in raw_image_names:
	
			#Open the current raw image (wait for it to load) and split the channels
			current_raw_image = IJ.openImage(os.path.join(raw_temp_directory, raw_image_name))
			current_raw_image.show()
			image_opened = WindowManager.getWindow(raw_image_name)
			while image_opened==None:
				time.sleep(0.5)
			IJ.run("Split Channels")
			
			#Select the PLA channel (user gives the number), make a Z-projection (makes another image), and threshold it (doesn't create a third image) 
			IJ.selectWindow(PLA_channel)
			current_PLA_channel = IJ.getImage()
			IJ.run("Z Project...", "projection=[Max Intensity]")
			MAX_PLA_channel = IJ.getImage()
			IJ.setAutoThreshold(MAX_PLA_channel, threshold_method + " dark")
			IJ.run(MAX_PLA_channel, "Convert to Mask", "")
			thresholded_PLA_channel = IJ.getImage()
			
			#Make directories and names to save the PLA channels
			save_PLA_directory = raw_temp_directory.replace(raw_image_directory, os.path.join(analysis_directory, "PLA_channels"))
			save_PLA_name = os.path.join(save_PLA_directory, os.path.splitext(raw_image_name)[0])
			if not os.path.exists(save_PLA_directory):
				os.makedirs(save_PLA_directory)
	
			#Save PLA channel, wait 3 seconds, close all the windows and flush memory
			IJ.saveAs(thresholded_PLA_channel, "Tiff", save_PLA_name)
			print("Thresholded image: ", raw_image_name)
			time.sleep(3)
			IJ.run("Close All")
			IJ.run("Collect Garbage", "")

###################################################################################################################################################################
################################################ PLA quantification (Measure cell area + Analyze Particles) #######################################################

if Quantification==True:

	#There MUST be a subfolder called ROIs_analyzed in the folder Analysis with the same directory structure as the PLA_channels
	ROIs_analyzed = os.path.join(analysis_directory, "ROIs_analyzed")
	thresholded_PLA_channels = os.path.join(analysis_directory, "PLA_channels")

	#Walk through the raw image folder in case files or subfolders are used
	for PLA_temp_directory, subfolder, PLA_image_names in os.walk(os.path.join(analysis_directory, "PLA_channels")):
		PLA_image_names.sort()
	
		#Iterate through each PLA image 
		for PLA_image_name in PLA_image_names:

			#For each PLA thresholded image, there must be a folder with the same name containing the ROIs to analyze for that image
			PLA_ROIs_folder = os.path.join(PLA_temp_directory.replace(thresholded_PLA_channels, ROIs_analyzed), os.path.splitext(PLA_image_name)[0])
			
			#Iterate through each PLA ROI (of each raw image)
			for PLA_ROI_directory, subfolder2, PLA_ROIs in os.walk(PLA_ROIs_folder):
				for PLA_ROI in PLA_ROIs:
					
					#Open the current PLA image
					current_PLA_image = IJ.openImage(os.path.join(PLA_temp_directory, PLA_image_name))
					current_PLA_image.show()
					image_opened = WindowManager.getWindow(PLA_image_name)

					#If the image is big and heavy, ImageJ will take a moment to open it, so we delay the script to wait for it
					while image_opened==None:
						time.sleep(0.5)

					#Load the ROI manager and open the current ROI
					rm = RoiManager()
					current_PLA_ROI_directory = os.path.join(PLA_ROI_directory, PLA_ROI)
					rm.runCommand("Open", str(current_PLA_ROI_directory))
					rm.select(0)
						
					#Get the area of the ROI
					rm.runCommand("Measure")
				
					#Analyze particles to count PLA puncta which meet the size criteria
					IJ.selectWindow(1)
					IJ.run("Analyze Particles...", "size=0.1-1000 summarize")
					print("Quantified cell: ", PLA_ROI)
					current_PLA_image.close()
					rm.close()
					IJ.run("Collect Garbage", "")

	#Save the results
	if not os.path.exists(os.path.join(analysis_directory, "Output_files")):
		os.makedirs(os.path.join(analysis_directory, "Output_files"))
	IJ.saveAs("Results", str(os.path.join(analysis_directory, "Output_files", "Measures")) + ".csv")
	IJ.selectWindow("Results")
	IJ.run("Close")
	IJ.selectWindow("Results")
	IJ.saveAs("Results", str(os.path.join(analysis_directory, "Output_files", "Particles")) + ".csv")
	IJ.run("Close")

###################################################################################################################################################################

#Finish the timer and print times
ending_time = datetime.now()
print("Script started on:", starting_time, " Script finished on:", ending_time)

###################################################################################################################################################################
###################################################################################################################################################################
###################################################################################################################################################################

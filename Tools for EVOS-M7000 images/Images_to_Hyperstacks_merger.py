###############################################################################################################################################################
###############################################################################################################################################################
###############################################################################################################################################################
'''

Full name of script: Hyperstack generator for EVOS M700 images [Version 01]

Script languague: Jython (Python wrapper for Java, run with ImageJ/Fiji app -not pyImageJ-)

Description: The EVOS M7000 imager does not save the images acquired in a bioformat, everything is saved as .TIFF and it gives the raw data as individual
             images of slices (if z-stack was acquired), for each channel, for each field of view, for each area. This script allows to make a single file
             by stacking each slice of the stack for each channel and merging them + assigning colours. The output is .TIFF hyperstacks with simplified
             file names based on the field of view imaged (FOV).

Made by: Eduardo Reyes Alvarez

Contact: eduardo_reyes09@hotmail.com

Last update: March 28, 2022

Version History:
V01 (Mar 28, 2022): First working version of the script, it works but doesnt stack, merge and save the very last image. Code not fully annotated.
V02 (Mar 28, 2022): Several conditions and specific cases implemented, now it works for all images. It works for 1 or more channels but needs manual changes.
V03 (Apr 01, 2022): Works with any number of channels and order (selected by user menu). Code fully annotated.

'''

###############################################################################################################################################################
########################################## Import neccesary packages and make the interactive menu ############################################################

import os
import time
from datetime import datetime
from ij import IJ, ImagePlus
from ij import WindowManager
from ij.plugin.frame import RoiManager
from ij.gui import Roi

#@ File    (label = "Raw Image folder", style = "directory") raw_image_directory
#@Boolean   (label="Crop cells", style = "checkbox") Crop_cells

#Start the timer
starting_time = datetime.now()


#Get full path of raw images and the cells folder from the menu
raw_image_directory = raw_image_directory.getAbsolutePath()

###############################################################################################################################################################
####################################################### Scan all the images in the directory ##################################################################

image_data = []

#Walk through the raw image folder (NO subfolders!)
for directory, subfolder, raw_images in os.walk(raw_image_directory):
	for image in raw_images:
			
		#Remove the .tif from the name
		trimmed_image_name = os.path.splitext(image)[0]
			
		#Remove the left side of the name, from the resulting string, first 2 numbers are slice number, last is channel number
		trimmed_image_name = trimmed_image_name.split("_p00_z")[1]
		channel = trimmed_image_name[-1]
		zslice = trimmed_image_name[0:2]
			
		#Since the FOV can be 2 or 3 numbers, we get it by trimming on the delimitors f__d
		trimmed_image_name = trimmed_image_name.split("d")[0]
		FOV = trimmed_image_name.split("f")[1]

		#Now we append the info of the current image to our list, transforming the strings to integers for later processing
		image_data.append([os.path.join(directory, image), int(FOV), int(channel), int(zslice)])

#Once the data from all images has been extracted, we sort by FOV, then by channel, then by slice
image_data.sort(key = lambda x : (x[1], x[2], x[3]))
	
#Optional
for i in image_data:
	print("FOV:", i[1], "Channel:", i[2], "Slice:", i[3])

#We can retrieve the total number of FOVs, channels and slides from the very last image processed
#These will be used to loop when opening the images to make stacks
total_FOVs = image_data[-1][1]
total_channels = image_data[-1][2]
total_slices = image_data[-1][3]

###############################################################################################################################################################
############################################################### Open images and make stacks ###################################################################

control_FOV = 0
control_channels = 0

#Open all the slices for each channel of each FOV
for image_index, image_info in enumerate(image_data):

	#
	current_FOV = image_info[1]
	current_channel = image_info[2]

	#This will make require to include PLA in all the image names
	if control_FOV != current_FOV or control_channels != current_channel:
		IJ.run("Images to Stack", "name=Stack title=PLA use")
		stack = WindowManager.getImage("Stack")
		stack.setTitle("Stack_channel_" + str(control_channels))
		control_channels = current_channel
		IJ.run("Collect Garbage", "")

		#This needs to be adjusted if the number of channels is different than 3, and the order depending the acquisition
		if control_FOV != current_FOV:
			IJ.run("Merge Channels...", "c1=[Stack_channel_2] c2=[Stack_channel_1] c3=[Stack_channel_0] create")
			time.sleep(0.5)
			IJ.selectWindow("Composite")
			hyperstack = IJ.getImage()
			FOV_saving_path = os.path.join(os.path.split(image_info[0])[0], "Merged", "FOV_"+str(control_FOV))
			IJ.saveAs(hyperstack, "Tiff", FOV_saving_path)
			print("Fields of view completed:", control_FOV, "/", total_FOVs) 
			time.sleep(3)
			IJ.run("Close All")
			IJ.run("Collect Garbage", "")
			control_FOV = current_FOV

	#Open image
	current_raw_image = IJ.openImage(image_info[0])
	current_raw_image.show()
	image_opened = WindowManager.getWindow(os.path.split(image_info[0])[1])

	#If the image is big and heavy, ImageJ will take a moment to open it, so we delay the script to wait for it
	while image_opened==None:
		time.sleep(0.1)
	print("Image:", image_index+1, "/", len(image_data))


###############################################################################################################################################################

#Finish the timer and print processing time
ending_time = datetime.now()
processing_time = (ending_time.getTime() - starting_time.getTime())/1000.000000
print("Images processed:", len(image_data), "Script processing time (min):", processing_time/60)

###############################################################################################################################################################
###############################################################################################################################################################
###############################################################################################################################################################

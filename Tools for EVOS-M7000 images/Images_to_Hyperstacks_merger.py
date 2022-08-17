###############################################################################################################################################################
###############################################################################################################################################################
###############################################################################################################################################################
'''

Full name of script: Hyperstack generator for EVOS M700 images [Version 03]

Script languague: Jython (Python wrapper for Java, run with ImageJ/Fiji app -not pyImageJ-)

Description: The EVOS M7000 imager does not save the images acquired in a bioformat, everything is saved as .TIFF and it gives the raw data as individual
             images of slices (if z-stack was acquired), for each channel, for each field of view, for each area. This script allows to make a single file
             by stacking each slice of the stack for each channel and merging them + assigning colours. The output is .TIFF hyperstacks with simplified
             file names based on the field of view imaged (FOV).

Made by: Eduardo Reyes Alvarez

Contact: eduardo_reyes09@hotmail.com

Last update: Apr 01, 2022

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
#@ String (visibility=MESSAGE, value="For Brightfield select Gray (check images are saved as Mono and not RGB)", required=false) msg1
#@ String (visibility=MESSAGE, value="Note: The EVOS starts counting the channels from 0", required=false) msg2
#@String   (label = "Channel 0 colour: ", style = "listBox", choices = { "", "Red", "Green", "Blue", "Gray", "Cyan", "Magenta" }) ch0_color
#@String   (label = "Channel 1 colour: ", style = "listBox", choices = { "", "Red", "Green", "Blue", "Gray", "Cyan", "Magenta" }) ch1_color
#@String   (label = "Channel 2 colour: ", style = "listBox", choices = { "", "Red", "Green", "Blue", "Gray", "Cyan", "Magenta" }) ch2_color
#@String   (label = "Channel 3 colour: ", style = "listBox", choices = { "", "Red", "Green", "Blue", "Gray", "Cyan", "Magenta" }) ch3_color
#@String   (label = "Channel 4 colour: ", style = "listBox", choices = { "", "Red", "Green", "Blue", "Gray", "Cyan", "Magenta" }) ch4_color
#@String   (label = "Image name keyword") name_key
#@ String (visibility=MESSAGE, value="Script made by: Eduardo Reyes-Alvarez", required=false) msg3


#Start the timer
starting_time = datetime.now()

#Get full path of raw images and the cells folder from the menu
raw_image_directory = raw_image_directory.getAbsolutePath()

###############################################################################################################################################################
####################################################### Retrieving information of raw images ##################################################################

#From the directory obtained in the input, we will scan all images and extract information from their name to sort, group, and open in order

#The EVOS M700 saves the images in this format, which is retrieved as a string: ExperimentName_Bottom Slide_R_p00_z00_0_A00f00d0.tif
	#The R means Raw (could be M for Merged or something else)
	#The p00 might be for time lapses, as well as the _0_
	#The z00 is the slice number, usually two numbers from 00 to 20 or 30 (99 or 3 numbers almost never)
	#The A00 is the areas imaged. For a channel slide could vary from 00-05 (6 channels) but it is recommended to acquire and save one at the time
	#The f00 is the number of fields of view imaged, and could  be 2 or 3 numbers (depending on settings 00-999)
	#The d0 is the number of channel, which can be 0-4 given the capabilities of the equipment

#We will collect all the image information as sublists in this list
images_data = []

#Walk through all the images in the raw image folder (The only subfolder allowed MUST be named Merged and MUST be empty)
for directory, subfolder, raw_images in os.walk(raw_image_directory):
	for image in raw_images:
		
		#Get the name of the current image and remove the .tif from the name
		trimmed_image_name = os.path.splitext(image)[0]
			
		#Remove the left side of the name delimited by _p00_z, to get something like: 00_0_A00f00d00
		trimmed_image_name = trimmed_image_name.split("_p00_z")[1]
		
		#The last number is the channel number
		channel = trimmed_image_name[-1]

		#The first 2 numbers now correspond to the slice number
		zslice = trimmed_image_name[0:2]
			
		#Since the FOV can be 2 or 3 numbers, we get it by trimming whatever is between the delimitors f__d
		trimmed_image_name = trimmed_image_name.split("d")[0]
		FOV = trimmed_image_name.split("f")[1]

		#Now we append a list with the info of the current image to our main list, transforming the strings to integers to make processing easier
		images_data.append([os.path.join(directory, image), int(FOV), int(channel), int(zslice)])

#Once the data from all images has been extracted, we sort by FOV, then by channel, then by slice
images_data.sort(key = lambda x : (x[1], x[2], x[3]))
	
#We print the FOV, channel and slice extracted from the images as a control in case there is an error or mismatch 
for i in images_data:
	print("FOV:", i[1], "Channel:", i[2], "Slice:", i[3])

#Retrieve the total number of FOVs for progress print statements
total_FOVs = images_data[-1][1]

#Based on the input from the user, we get ready the variable to pass the channels to merge (if needed)
channels_to_merge = ""
total_channels = 5
#Iterate through the dropdowns displayed to the user
for i,color_input in enumerate([ch0_color, ch1_color, ch2_color, ch3_color, ch4_color]):
	#If the user didn't select anything, we have one less channel in total
	if color_input == "":
		total_channels = total_channels - 1
		continue
	#If the user selected a color, we iterate through the options we showed in the menu to find it
	for ii, color_option in enumerate(["Red", "Green", "Blue", "Gray", "Cyan", "Magenta"]):
		#Once we find what the color of each "...d" number of the images will be, we add it to the merge command
		if color_input == color_option:
			channels_to_merge = channels_to_merge + ("c"+str(ii+1)+"=[Stack_channel_"+str(i)+"] ")
			break

#We also make a subdirectory in the folder to save all the hyperstacks made
hyperstack_saving_path = os.path.join(raw_image_directory + "_Merged")
if not os.path.exists(hyperstack_saving_path):
	os.makedirs(hyperstack_saving_path)

###############################################################################################################################################################
#############################################################  Deciding the action to do for each image #######################################################

#The previous section produces a list where all the slices for each channel for one FOV are ordered together, then next channel and so on, same for next FOV
#We need to open all the images no matter what, we just need to decide when to do the stacking and merging+saving

#We will use some control variables to notice when the current image corresponds to a different channel or FOV
#For several exceptions, it is better to retrieve the first FOV and channel from the first image in our list
control_FOV = images_data[0][1]
control_channel = images_data[0][2]
image_index = 0

#In this loop we decide whether something is needed before opening an image (for the very 1st image, we compare to the control variables above)
#Since we open the image at the very end of the loop, we need to enter one more time after the last picture was open, so we can stack, merge and save
while image_index <= len(images_data):

	#First, we get the list of directory, FOV, Ch, Slice for the current image
	#The conditional here avoids an error once the image index is out of range of the image data elements
	image_info = images_data[image_index] if image_index < len(images_data) else images_data[image_index-1]

	#We extract the working FOV and channel for simplicity
	current_FOV = image_info[1]
	current_channel = image_info[2]

	#Second, we check whether we need to make a stack right now (when Ch or FOV change or when we are in the very last image 
	if control_FOV != current_FOV or control_channel != current_channel or image_index == len(images_data):
		#If true, we make a stack selecting only newly opened images (with a string in the name) so we leave untouched existing stacks for other channels
		IJ.run("Images to Stack", "name=Stack title="+name_key+" use")                                                          
		stack = WindowManager.getImage("Stack")
		stack.setTitle("Stack_channel_" + str(control_channel))

		#If we did a stack then we are done with the previous channel and we need to update the control channel to be aware of future changes
		control_channel = current_channel

		#Since we combined lots of images into one (still existing), we empty some memory (may not be much)
		IJ.run("Collect Garbage", "")

		#Third, if the info of the image to be opened corresponds to a new FOV (or it is the very last image), merge all channels if needed, save and close
		if control_FOV != current_FOV or image_index == len(images_data):

			#If we only have one channel, we don't need to run the merge plugin (will cause an error)
			if total_channels > 1:        
				IJ.run("Merge Channels...",  channels_to_merge+"create")
				#A small placeholder just in case it is too heavy
				time.sleep(0.5)

				#We select and get the merge before saving it
				IJ.selectWindow("Composite")
				hyperstack = IJ.getImage()
				
			#We save the stack or hyperstack
			save_FOV_as = os.path.join(hyperstack_saving_path, "FOV_"+str(control_FOV))
			image_to_save = hyperstack if total_channels > 1 else stack
			IJ.saveAs(image_to_save, "Tiff", save_FOV_as)

			#We print a counter to keep track of the progress with total number of FOVs and add a placeholder of 3s (for heavy images or slow computers)
			print("Fields of view completed:", control_FOV+1, "/", total_FOVs+1) 
			time.sleep(3)

			#Once saved, we close everything, reset the memory and update the control FOV before opening the image
			IJ.run("Close All")
			IJ.run("Collect Garbage", "")
			control_FOV = current_FOV

			#After the final image is saved, we no longer need the loop so we exit it to prevent errors
			if image_index == len(images_data):
				break
	
	#Fourth, once we collect the info, check for new stack, and check for new FOV... we open, show and get the current image
	current_raw_image = IJ.openImage(image_info[0])
	current_raw_image.show()
	image_opened = WindowManager.getWindow(os.path.split(image_info[0])[1])

	#If the image is heavy or PC resources low, ImageJ will take a moment to open it, so we use a placeholder checking every 0.1s until is open
	while image_opened==None:
		time.sleep(0.1)
	
	#We print a counter to keep track of the progress for the images processed vs the total in the folder, and update the image index
	print("Image:", image_index+1, "/", len(images_data))
	image_index = image_index + 1

######################################################################### End of the script ###################################################################

#Finish the timer and get the total number of seconds spent
ending_time = datetime.now()
processing_time = (ending_time.getTime() - starting_time.getTime())/1000.00

#Print a summary of the work done and time it required
print("Images processed:", len(images_data), "Hyperstacks made:", total_FOVs+1, "Script processing time (min):", round(processing_time/60, 1))

###############################################################################################################################################################
###############################################################################################################################################################
###############################################################################################################################################################

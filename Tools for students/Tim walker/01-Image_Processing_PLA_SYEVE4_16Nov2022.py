############################################################################################################################################################
'''

Full name of script: Image processing for PLA experiment in EV and E4 TMEM127 KO SH-SY5Y cells  [Version 01]

Script languague: Jython (Python wrapper for Java, run with ImageJ/Fiji app -not pyImageJ-)

Description: This script processess the output images of the EVOS-M7000 when doing Proximity Ligation Assays (PLA) on Ibidi uSlides 0.4 and imaged with the
             automation tool of the imager. This script does 4 main steps, 1)Merges the output images back to hyperstacks, 2)Renames the merged images so it is
             easier to stitch them, 3)Stitches 7 by 5 fields together, 4)Makes a Z-projection of the stitched images for quantification purposes. 
             
             NOTE: This is an adaptation of another script (https://github.com/EdRey05/Tools for students/Eduardo Reyes/Image_Processing_SYTTMZ_automated_PLA.py) 
                   with few modifications to make it stitch the number of fields acquired in this specific channel slide (15 columns by 40 rows = 600 FOVs with
                   3 slices each, ~25% of area). Only 3 folders of this batch were processed with this script (syPLA1 - RET-AP2).

Made by: Eduardo Reyes Alvarez

Contact: eduardo_reyes09@hotmail.com

Last update: November 16, 2022

Version History:
V01 (November 16, 2022): First version of the script adapted to a bigger area (600 fields) for this experiment. The logic of the script did not change, 
						 for more information check the description of the first script of this kind, referenced above (the annotations in the code are
						 exactly the same).

'''

############################################################################################################################################################
############################################################################################################################################################
########################################## Import neccesary packages and make the interactive menu #########################################################

import os
import time
from datetime import datetime
from ij import IJ, ImagePlus
from ij import WindowManager
from ij.plugin.frame import RoiManager
from ij.gui import Roi

#@ File    (label = "Experiment folder", style = "directory") experiment_directory
#@ String (visibility=MESSAGE, value="For Brightfield select Gray (check images are saved as Mono and not RGB)", required=false) msg1
#@ String (visibility=MESSAGE, value="Note: The EVOS starts counting the channels from 0", required=false) msg2
#@String   (label = "Channel 0 colour: ", style = "listBox", choices = { "", "Red", "Green", "Blue", "Gray", "Cyan", "Magenta" }) ch0_color
#@String   (label = "Channel 1 colour: ", style = "listBox", choices = { "", "Red", "Green", "Blue", "Gray", "Cyan", "Magenta" }) ch1_color
#@String   (label = "Channel 2 colour: ", style = "listBox", choices = { "", "Red", "Green", "Blue", "Gray", "Cyan", "Magenta" }) ch2_color
#@String   (label = "Channel 3 colour: ", style = "listBox", choices = { "", "Red", "Green", "Blue", "Gray", "Cyan", "Magenta" }) ch3_color
#@String   (label = "Channel 4 colour: ", style = "listBox", choices = { "", "Red", "Green", "Blue", "Gray", "Cyan", "Magenta" }) ch4_color
#@String   (label = "Image name keyword") name_key
#@ String (visibility=MESSAGE, value="Specify below the rows to stitch (all columns will be used)", required=false) msg3
#@ Integer (label="Columns", style="slider", min=1, max=10, stepSize=1) grid_size_x
#@ Integer (label="Rows", style="slider", min=1, max=10, stepSize=1) grid_size_y1
#@ String (visibility=MESSAGE, value="If the rows above gives an uneven number of residual rows, specify here:", required=false) msg4
#@ Integer (label="Rows (last image)", style="slider", min=1, max=10, stepSize=1) grid_size_y2
#@ Integer (label="Tile overlap (%)", min=1, max=100, value=20) tile_overlap
#@ String (visibility=MESSAGE, value="Numbers separated by comma (0,35,70...)", required=false) msg5
#@ String (label="First image of each area to stitch", description="Name field") stitching_index
#@ Integer (label="Rolling radius (for background subtraction):", min=1, max=1000, description="Test this number beforehand", value=100) background_radius
#@ String (visibility=MESSAGE, value="Script made by: Eduardo Reyes-Alvarez", required=false) msg6

#Start the MAIN timer
whole_script_starting_time = datetime.now()

#Get full path of raw images and the cells folder from the menu
experiment_directory = experiment_directory.getAbsolutePath()

############################################################################################################################################################
########################################## PART 1 - MERGE TOGETHER THE IMAGES TO MAKE HYPERSTACKS ##########################################################

####################################################### Retrieving information of raw images ###############################################################

#Start the timer
starting_time = datetime.now()

#Get full path of where to look for the raw images
raw_image_directory = os.path.join(experiment_directory, "Raw Images")

#From the directory obtained in the input, we will scan all images and extract information from their name to sort, group, and open in order

#The EVOS M700 saves the images in this format, which is retrieved as a string: ExperimentName_Bottom Slide_R_p00_z00_0_A00f00d0.tif
	#The R means Raw (could be M for Merged or something else)
	#The p00 might be for time lapses, as well as the _0_
	#The z00 is the slice number, usually two numbers from 00 to 20 or 30 (99 or 3 numbers almost never)
	#The A00 is the areas imaged. For a channel slide could vary from 00-05 (6 channels) but it is recommended to acquire and save one at the time
	#The f00 is the number of fields of view imaged, and could  be 2 or 3 numbers (depending on settings 00-999)
	#The d0 is the number of channel, which can be 0-4 given the capabilities of the equipment

#Collect all the image information as sublists in this list
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

		#Append a list with the info of the current image to our main list, transforming the strings to integers to make processing easier
		images_data.append([os.path.join(directory, image), int(FOV), int(channel), int(zslice)])

#Once the data from all images has been extracted, sort by FOV, then by channel, then by slice
images_data.sort(key = lambda x : (x[1], x[2], x[3]))
	
#Print the FOV, channel and slice extracted from the images as a control in case there is an error or mismatch [No longer needed but left here]
#for i in images_data:
#	print("FOV:", i[1], "Channel:", i[2], "Slice:", i[3])

#Retrieve the total number of FOVs for progress print statements
total_FOVs = images_data[-1][1]

#Based on the input from the user, get the variable ready to pass the channels to merge (if needed)
channels_to_merge = ""
total_channels = 5
#Iterate through the dropdowns displayed to the user
for i,color_input in enumerate([ch0_color, ch1_color, ch2_color, ch3_color, ch4_color]):
	#If the user didn't select anything, we have one less channel in total
	if color_input == "":
		total_channels = total_channels - 1
		continue
	#If the user selected a color, iterate through the options we showed in the menu to find it
	for ii, color_option in enumerate(["Red", "Green", "Blue", "Gray", "Cyan", "Magenta"]):
		#Once the color of each "...d" number of the images is known, add it to the merge command
		if color_input == color_option:
			channels_to_merge = channels_to_merge + ("c"+str(ii+1)+"=[Stack_channel_"+str(i)+"] ")
			break

#Make a subdirectory in the folder to save all the hyperstacks made
hyperstack_saving_path = os.path.join(raw_image_directory + "_Merged")
if not os.path.exists(hyperstack_saving_path):
	os.makedirs(hyperstack_saving_path)

############################################################ Deciding action to do for each image ##########################################################


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

	#Extract the working FOV and channel for simplicity
	current_FOV = image_info[1]
	current_channel = image_info[2]

	#Second, check whether we need to make a stack right now (when Ch or FOV change or when we are in the very last image 
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

				#Select and get the merge before saving it
				IJ.selectWindow("Composite")
				hyperstack = IJ.getImage()
				
			#Save the stack or hyperstack
			save_FOV_as = os.path.join(hyperstack_saving_path, "FOV_"+str(control_FOV))
			image_to_save = hyperstack if total_channels > 1 else stack
			IJ.saveAs(image_to_save, "Tiff", save_FOV_as)

			#Print a counter to keep track of the progress with total number of FOVs and add a placeholder of 3s (for heavy images or slow computers)
			print("Fields of view completed:", control_FOV+1, "/", total_FOVs+1) 
			time.sleep(3)

			#Once saved, close everything, reset the memory and update the control FOV before opening the image
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

	#If the image is heavy or PC resources low, ImageJ will take a moment to open it, so use a placeholder checking every 0.1s until is open
	while image_opened==None:
		time.sleep(0.1)
	
	#Print a counter to keep track of the progress for the images processed vs the total in the folder, and update the image index [No longer needed]
	#print("Image:", image_index+1, "/", len(images_data))
	image_index = image_index + 1

################################################################### End of the merging #####################################################################

#Finish the timer and get the total number of seconds spent
ending_time = datetime.now()
merging_time = (ending_time.getTime() - starting_time.getTime())/1000.00

#Print a summary of the work done and time it required
print("Images processed:", len(images_data), "Hyperstacks made:", total_FOVs+1, "Merging time (min):", round(merging_time/60, 1))


############################################################################################################################################################
######################################################## PART 2 - RENAME THE IMAGES FOR STITCHING ##########################################################

###################################### Create the sequence of re-ordered numbers and replace the current names #############################################

#To create this sequence, make an excel file with the acquisition info+grid, then copy+paste them here in the right order (Serpentine Vertical)
#This part only works for 15% of a channel slide at 40x from the center with more overlap, scanned serpentine vertically, needs manual edits for others
new_names = [ 0, 7, 14, 21, 28, 35, 42, 49, 56, 63, 70, 77, 84, 91, 98,  105, 112, 119, 126, 133, 140, 147, 154, 161, 168, 175,  182, 189, 196, 203, 210,
             217, 224, 231, 238, 245, 252, 259, 266, 273, 274, 267, 260, 253, 246, 239, 232, 225, 218, 211, 204, 197, 190, 183, 176, 169, 162, 155, 148,
             141, 134, 127, 120, 113, 106, 99, 92, 85, 78, 71, 64, 57, 50, 43, 36, 29, 22, 15, 8, 1, 2, 9, 16, 23, 30, 37, 44, 51, 58, 65, 72, 79, 86, 93,
             100, 107, 114, 121, 128, 135, 142, 149, 156, 163, 170, 177, 184, 191, 198, 205, 212, 219, 226, 233, 240, 247, 254, 261, 268, 275, 276, 269, 
             262, 255, 248, 241, 234, 227, 220, 213, 206, 199, 192, 185, 178, 171, 164, 157, 150, 143, 136, 129, 122, 115, 108, 101, 94, 87, 80, 73, 66, 
             59, 52, 45, 38, 31, 24, 17, 10, 3, 4, 11, 18, 25, 32, 39, 46, 53, 60, 67, 74, 81, 88, 95, 102, 109, 116, 123, 130, 137, 144, 151, 158, 165, 
             172, 179, 186, 193, 200, 207, 214, 221, 228, 235, 242, 249, 256, 263, 270, 277, 278, 271, 264, 257, 250, 243, 236, 229, 222, 215, 208, 201, 
             194, 187, 180, 173, 166, 159, 152, 145, 138, 131, 124, 117, 110, 103, 96, 89, 82, 75, 68, 61, 54, 47, 40, 33, 26, 19, 12, 5, 6, 13, 20, 27, 
             34, 41, 48, 55, 62, 69, 76, 83, 90, 97, 104, 111, 118, 125, 132, 139, 146, 153, 160, 167, 174, 181, 188, 195, 202, 209, 216, 223, 230, 237, 
             244, 251, 258, 265, 272, 279, 553, 546, 539, 532, 525, 518, 511, 504, 497, 490, 483, 476, 469, 462, 455, 448, 441, 434, 427, 420, 413, 406,
             399, 392, 385, 378, 371, 364, 357, 350, 343, 336, 329, 322, 315, 308, 301, 294, 287, 280, 281, 288, 295, 302, 309, 316, 323, 330, 337, 344, 
             351, 358, 365, 372, 379, 386, 393, 400, 407, 414, 421, 428, 435, 442, 449, 456, 463, 470, 477, 484, 491, 498, 505, 512, 519, 526, 533, 540, 
             547, 554, 555, 548, 541, 534, 527, 520, 513, 506, 499, 492, 485, 478, 471, 464, 457, 450, 443, 436, 429, 422, 415, 408, 401, 394, 387, 380,
             373, 366, 359, 352, 345, 338, 331, 324, 317, 310, 303, 296, 289, 282, 283, 290, 297, 304, 311, 318, 325, 332, 339, 346, 353, 360, 367, 374,
             381, 388, 395, 402, 409, 416, 423, 430, 437, 444, 451, 458, 465, 472, 479, 486, 493, 500, 507, 514, 521, 528, 535, 542, 549, 556, 557, 550,
             543, 536, 529, 522, 515, 508, 501, 494, 487, 480, 473, 466, 459, 452, 445, 438, 431, 424, 417, 410, 403, 396, 389, 382, 375, 368, 361, 354,
             347, 340, 333, 326, 319, 312, 305, 298, 291, 284, 285, 292, 299, 306, 313, 320, 327, 334, 341, 348, 355, 362, 369, 376, 383, 390, 397, 404,
             411, 418, 425, 432, 439, 446, 453, 460, 467, 474, 481, 488, 495, 502, 509, 516, 523, 530, 537, 544, 551, 558, 559, 552, 545, 538, 531, 524,
             517, 510, 503, 496, 489, 482, 475, 468, 461, 454, 447, 440, 433, 426, 419, 412, 405, 398, 391, 384, 377, 370, 363, 356, 349, 342, 335, 328,
             321, 314, 307, 300, 293, 286 ]
			  
#To avoid problems with natural sorting, we don't scan the folder with os.walk, instead, we know from the acquisition excel file what number was given and
#what number should be, so we just iterate through the indices of the list above, which we know goes 0...356, locate the corresponding image, and rename it
for old_index, new_index in enumerate(new_names):
	old_name = os.path.join(hyperstack_saving_path, ("FOV_"+str(old_index)+".tif"))
	new_name = os.path.join(hyperstack_saving_path, ("Image_"+str(new_index)+".tif"))
	os.rename(old_name, new_name)

print("Images succesfully renamed and ready for stitching...")


############################################################################################################################################################
################################################################# PART 3 - STITCHING #######################################################################

################################################## Stitching FOVs using the ImageJ plug-in "Grid-stitching" ################################################

'''
For a 8gb RAM PC, solely running ImageJ with 7.5gb in Memory & threads, a maximum of ~42 FOVs with 3 colours and 6 slices can be stitched together.
Usually in Ibidi channel slides with automated imaging on the EVOS M7000 we have a small number of colums (4-8) and a big number of rows (like 50).
This part of the script was designed to stitch big images using all columns with user-defined number of images and rows, for example, if the user only gives
index of first images 0 and 35, with 7 cols and 5 rows, the result would be only 2 images (7 by 5) even if there are more images to use in the _Merged
folder. The only exception is when we have a non-easy to evenly divide the rows, for example, if we have 51, it is easy to do 10 images with 5 rows each,
but we will have an extra row. For this reason, the script asks for the number of rows for the last image, so we can do 9 images 7 by 5, and the last 7 by 6
to use all data available. Note that the maximum for the 7-8gb of RAM would be around 42 images, so we could not make 5 images 7 by 10.

Until 2022, ImageJ comes with a plug-in called Grid Stitching included. The settings below correspond to selecting in this plug-in's menu Grid row by row,
up and down, the size of the grid and overlap is asked to the user, the fusion method is linear blending with the parameters given by default (regression
threshold 0.3, max/avg displacement threshold 2.5, and absolute displacement threshold 3.5) -these numbers were not adjusted/tested in more detail due to 
time constraints-. Also, this code will save each slice stitched of each channel directly to the directory without showing the result (until the part 4).
'''

#Start the timer
starting_time = datetime.now()

#Make folder to save stitched images
stitching_saving_path = os.path.join(experiment_directory, "Raw Images_Stitched")
if not os.path.exists(stitching_saving_path):
	os.makedirs(stitching_saving_path)

####################################################### Retrieving information of raw images ###############################################################

#Prepare the directory from a os.path to what is required for the stitching  plug-in
data_directory = str(experiment_directory).replace("\\", "/")

#Make a list of all the indeces of the first images to be stitched (given by the user, depends on how many want to be stitched together)
first_image_index = stitching_index.split(",")
merges_name = "Image"

#Iterates to make big images starting in the given numbers
for i,index in enumerate(first_image_index):

	#Make a parcial time tracker to print how long it takes for each image to stitch (plus the whole stitching part separately)
	parcial_time1 = datetime.now()
	
	#Pass the amount of rows that will be stitched together, which may be variable             
	grid_size_y = grid_size_y1 if i<len(first_image_index)-1 else grid_size_y2

	#Make sure to clear the memory to handle this much data processing
	IJ.run("Collect Garbage", "")
	time.sleep(5)
	IJ.run("Collect Garbage", "")
	
	#Pass all the information needed for the Grid Stitching plug-in, which will save each slice for each channel separately without showing it
	IJ.run("Grid/Collection stitching", "type=[Grid: row-by-row] order=[Right & Down                ] "+
		   "grid_size_x="+str(grid_size_x)+" grid_size_y="+str(grid_size_y)+
		   " tile_overlap="+str(tile_overlap)+" first_file_index_i="+index+
		   " directory=["+data_directory+"/Raw Images_Merged] file_names="+merges_name+"_{i}.tif"+
		   " output_textfile_name=TileConfiguration.txt fusion_method=[Linear Blending] regression_threshold=0.30"+
		   " max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50"+
		   " computation_parameters=[Save memory (but be slower)] image_output=[Write to disk] output_directory=["+data_directory+"/]")
	
	#Wait a bit after the calculations are done
	time.sleep(5)
	
	#Locate each of the slices that the plug-in produced. This part requires manual edits if a number of slices is different than 4 (current).
	#Add/delete for each colour the number of slices required, following the name format as below. This plug-in does C1=red, C2=green, C3=blue.
	#For a 1/2 color image stitching, remove the corresponding list(s).
	red_slices = [data_directory+"/img_t1_z1_c1",
                data_directory+"/img_t1_z2_c1",
                data_directory+"/img_t1_z3_c1"]
	
	green_slices = [data_directory+"/img_t1_z1_c2",
                  data_directory+"/img_t1_z2_c2",
                  data_directory+"/img_t1_z3_c2"]
	
	blue_slices = [data_directory+"/img_t1_z1_c3",
                 data_directory+"/img_t1_z2_c3",
                 data_directory+"/img_t1_z3_c3"]
	
	#Prepare to open the stitched slices			   
	IJ.run("Collect Garbage", "")
	time.sleep(5)
	
	#Iterate through the lists above. This step also requires manual edits for 1/2 colour images.
	for ii, channel in enumerate([red_slices, green_slices, blue_slices]):
		colour_order = ["Red", "Green", "Blue"]
	
		#Open all the slices for the current channel and let them load properly
		for channel_slice in channel:
			current_slice = IJ.openImage(channel_slice)
			while current_slice==None:
				time.sleep(0.1)
			current_slice.show()
			time.sleep(3)
	
		#Make a stack for the current channel, wait and free any memory we can get
		IJ.run("Images to Stack", "name=Stack_"+colour_order[ii]+" title=img use")  
		time.sleep(10)                                                        
		IJ.run("Collect Garbage", "")
	
	#Once the stacks for all the channels are ready, merge them. This step also requires manual edits for images with only 1/2 channels.
	IJ.run("Merge Channels...",  "c1=Stack_Red c2=Stack_Green c3=Stack_Blue create")
	time.sleep(10)
	IJ.run("Collect Garbage", "")
	
	#Get the merged image into a variable
	IJ.selectWindow("Composite")
	Stitched_image = IJ.getImage()
	
	#Save the merged image with just an ascending number (does not especify yet which rows were used for it, that comes next)
	IJ.saveAs(Stitched_image, "Tiff", os.path.join(stitching_saving_path, "Row_"+str(i+1)+".tif"))   
	time.sleep(20)
	Stitched_image.close()
	IJ.run("Collect Garbage", "")
	
	#Remove this output slices once they have been merged, coloured and saved, so we don't have issues in case there are more/less in other folders
	for slice_generated in (red_slices + green_slices + blue_slices):
		os.remove(slice_generated)
	IJ.run("Collect Garbage", "")
	
	#Parcial timer and a progress update for each stitched image                                 
	parcial_time2 = datetime.now()
	progress_time = (parcial_time2.getTime() - parcial_time1.getTime())/1000.00
	print("Images stitched: ", i+1, "  Processing time for this image: ", round(progress_time/60, 1))

#Make a list with the names we want on our stitched images. This part also requires manual edits if not used these numbers of rows.
stitched_names = ["Row_01_05", "Row_06_10", "Row_11_15", "Row_16_20", "Row_21_25", "Row_26_30", "Row_31_35", "Row_36_40", 
                  "Row_41_45", "Row_46_50", "Row_51_55", "Row_56_60", "Row_61_65", "Row_66_70", "Row_71_75", "Row_76_80"]

#Iterate through the images saved above and rename them.
for iii, name in enumerate(stitched_names):
	old_name = os.path.join(stitching_saving_path, "Row_"+str(iii+1)+".tif")
	new_name = os.path.join(stitching_saving_path, name+".tif")
	os.rename(old_name, new_name)

################################################################### End of the stitching ###################################################################

#Finish the timer and get the total number of seconds spent
ending_time = datetime.now()
stitching_time = (ending_time.getTime() - starting_time.getTime())/1000.00

#Print a summary of the work done and time it required
print("Total stitching time (min):", round(stitching_time/60, 1))


############################################################################################################################################################
################################################## PART 4 - MAKE PROJECTION AND SUBTRACT BACKGROUND ########################################################

######################################################### Make Z-projection for data analysis ##############################################################

#Start the timer
starting_time = datetime.now()

#Make folder to save the processed images
projections_saving_path = os.path.join(experiment_directory, "Processed Images for Analysis")
if not os.path.exists(projections_saving_path):
	os.makedirs(projections_saving_path)

#Scan the folder were all the stitched images are
for folder, subfolder, stitched_images in os.walk(stitching_saving_path):
	
	#Iterate through the stitched images
	for stitched_image in stitched_images:
		
		#Open a stitched image (these are heavy, 1-3gb so they need longer to load)
		original_image = IJ.openImage(os.path.join(folder, stitched_image))
		while original_image==None:
			time.sleep(1)
		original_image.show()
		
		#Make the Z-projection
		IJ.run("Z Project...", "projection=[Max Intensity]")
		
		#Close the original -heavy- image and clear some memory
		original_image.close()
		time.sleep(2)
		IJ.run("Collect Garbage", "")
		time.sleep(5)
		IJ.run("Collect Garbage", "")
		
		#Subtract the background to clean the image and improve contrast
		projected_image = IJ.getImage()
		IJ.run("Subtract Background...", "rolling="+str(background_radius))
		projected_image = IJ.getImage()

		#Save the projection
		projections_saving_name = os.path.join(projections_saving_path, projected_image.getTitle())
		IJ.saveAs(projected_image, "Tiff", projections_saving_name)
		time.sleep(10)
		
		#Close the image and clear the memory
		projected_image.close()
		time.sleep(2)
		IJ.run("Collect Garbage", "")
		time.sleep(5)
		IJ.run("Collect Garbage", "")
		
		#Print the status of the process
		print("Image processed: ", stitched_image)

################################################################### End of the processing ##################################################################

#Finish the timer and get the total number of seconds spent
ending_time = datetime.now()
processing_time = (ending_time.getTime() - starting_time.getTime())/1000.00

#Print a summary of the work done and time it required
print("Stitched images processing time (min):", round(processing_time/60, 1))


############################################################################################################################################################
################################################################### End of the script ######################################################################

#Finish the MAIN timer and get the total number of seconds spent
whole_script_ending_time = datetime.now()
whole_script_running_time = (whole_script_ending_time.getTime() - whole_script_starting_time.getTime())/1000.00

#Print a summary of the work done and time it required
print("Whole script running time for one channel/condition (hours):", round(whole_script_running_time/3600, 1))


############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################

######################################################################################################################################################################################
'''

Full name of script: Proximity Ligation Assay (PLA) quantification  [Version 04]

Script languague: Jython (Python wrapper for Java, run with ImageJ/Fiji app -not pyImageJ-)

Description: Same as the previous versions, this script crops cells of interest from a bigger image and also quantifies the area of the cell and the number of puncta in that
             region of one of the channels (PLA channel). The quantification is done using the Analyze Particles plug-in of ImageJ and the source image could be either 
             thresholded by one of the pre-set methods on ImageJ, or by segmentation using the Find Maxima plug-in in ImageJ. It is recommended that the user runs some tests
             to decide what parameters to use for each experiment or experimental condition, since these may vary due to image quality, imaging settings, etc.
             This script works for a simplified structure folder> A main folder that will be selected in the interactive menu, inside of which there must be 2 folders, one 
             with any name (need to type the name in the menu) containing the images to crop/quantify, and another folder called "ROIs". Inside the ROIs folder there must be
             a folder "For Presentation" if we want to crop cells, and a folder "For Analysis" if we want to quantify the cells (or both). The directory structure of the 
             folder where the images to process are, must match the directory structure of the two sets of ROI folders.

Made by: Eduardo Reyes Alvarez

Contact: eduardo_reyes09@hotmail.com

Last update: December 11, 2022

Version History:
V01 (Jun 01, 2021): First working version of the script. Requires a specific folder structure and 2 sets of ROIs per cell of interest. Some outputs are optional
                    such as cropped images of each cell, each PLA channel thresholded and the actual quantification (excel files). Code fully annotated.
V02 (June 20, 2021): Fixed/improved some directory handling during the iterations. Some steps can be improved: data saving and iteration through the images + 
                     ROIs when the raw images are heavy.
V03 (Aug  21,2022): Changed the folder structure that the script requires (compared to the last 2 versions). Significant improvements to the image and ROI handling
                    to iterate through all the images without constantly closing and opening again. The quantification (Measure for area, and Analyze Particles) now
                    is optional and includes the option to do it with Find Maxima too. All the parameters needed for re-analysis are asked to the user through the menu
                    and the result tables were improved to merge all the parameters with their labels (image and ROI name) into a single csv file. For easy preview of
                    the results in case re-analysis with different parameters is needed, the script saves the colour-coded particle counts of the Analyze Particles 
                    plug-in (any black particles are not counted due to the initial parameters). 
                    Pending: Enclose code into a function to enable batch mode (multiple folders). Follow-up script using python-pptx to import all the cropped images
                    produced by this script for easier result presentation.
V04 (Dec 11, 2022): Added short parameter that needs to be passed on to the Analyze Particles plug-in for images that are calibrated in inches. Added option to pass a set
                    of particle size and circularity different for each method. Also, there is now a Colab notebook to generate a pptx from the outputs of this script.
'''

######################################################################################################################################################################################
################################################## Import neccesary packages and make the interactive menu ###########################################################################

import os
import time
import csv
from datetime import datetime
from ij import IJ, ImagePlus
from ij import WindowManager
from ij.measure import ResultsTable
from ij.plugin.frame import RoiManager
from ij.gui import Roi

#@ File    (label = "Experimental condition folder:", style = "directory") exp_condition_folder
#@ String  (label="Name of folder containing images to crop/quantify:", description="Name field") source_images_folder
#@ Integer (label = "PLA channel number", style = "slider", min=1, max=5, stepSize=1) PLA_channel
#@ String  (visibility=MESSAGE, value="Particle counting is usually improved by background subtraction with low radius", required=false) msg1
#@ Integer (label="Rolling radius for PLA background subtraction:", min=1, max=50, description="<10 recommended, test your images first", value=3) PLA_background_radius
#@ Boolean (label="Crop cells", style = "checkbox") Crop_cells
#@ String  (choices={"-", "Threshold + Analyze Particles", "Find Maxima + Analyze Particles", "Both"}, style="listBox") Quantification
#@ String  (visibility=MESSAGE, value="Parameters for quantification:", required=false) msg2
#@ String  (visibility=MESSAGE, value="For different size+circularity between methods, pass T first a comma and then FM", required=false) msg3
#@ String  (label="Particle size ", description="0-Infinity, 10-1000, etc.", value="3-Infinity") particle_sizes
#@ String  (label="Particle circuarity:", description="0.00-1.00", value="0.10-1.00") particle_circularity
#@ String  (label = "Threshold method (if selected)", style = "listBox", choices = { "-","Default", "Huang", "Intermodes","IsoData", "IJ_IsoData", "Li", "MaxEntropy", "Mean", "MinError", "Minimum", "Moments", "Otsu", "Percentile", "RenyiEntropy", "Shanbhag", "Triangle", "Yen"}) threshold_method
#@ Integer (label="Prominence for Maxima (if selected):", min=1, max=100000, description="Test this number in a subset of images beforehand", value=500) prominence
#@ String  (visibility=MESSAGE, value="Script made by: Eduardo Reyes-Alvarez", required=false) msg4

#Start the timer
whole_script_starting_time = datetime.now()

#Get full path of the folder containing the images and prepare the other directories
exp_condition_folder = exp_condition_folder.getAbsolutePath()
raw_image_directory =os.path.join(exp_condition_folder, source_images_folder)
ROIs_directory = os.path.join(exp_condition_folder, "ROIs")
summary_ppt_cells_directory = os.path.join(exp_condition_folder, "Cropped cells")


######################################################################################################################################################################################
############################################################ Crop all the individual cells from raw images (Optional) ################################################################

#If the raw cells are big images with multiple cells, this section will be done for data/results presentation. If not needed, then uncheck the box and proceed to the next section
if Crop_cells==True:
    cropped_cells_directory = os.path.join(summary_ppt_cells_directory, "Fluorescence")
    if not os.path.exists(cropped_cells_directory):
        os.makedirs(cropped_cells_directory)
    presentation_ROIs_directory = os.path.join(ROIs_directory, "For Presentation")
    
    #Initialize the ROI manager
    rm = RoiManager()
    
    #Walk through the raw image folder in case additional subfolders are used
    for raw_temp_directory, subfolder, raw_image_names in os.walk(raw_image_directory):
        raw_image_names.sort()
        
        #Iterate through each raw image 
        for raw_image_name in raw_image_names:
            
            #Since this version of the script works with Z-projected images, we need to trim the name of the images (MAX_Row_01_05.tif to find a folder Row_01_05)
            raw_image_original_name = raw_image_name.split("X_")[1]
            raw_image_original_name = raw_image_original_name.split(".t")[0]
            
            #Find the folder with the ROIs for the current raw image
            ROIs_to_crop_folder = os.path.join(presentation_ROIs_directory, raw_image_original_name)
            
            #Now we're ready to open the current raw image 
            current_raw_image = IJ.openImage(os.path.join(raw_temp_directory, raw_image_name))
            while current_raw_image==None:
                time.sleep(0.5)
            current_raw_image.show()
            
            #Walk through the ROIs folder to get all the ROIs
            for ROI_temp_directory, subfolder2, ROIs in os.walk(ROIs_to_crop_folder):
                ROIs.sort()
                
                #Iterate through each ROI (for the current opened image)
                for ROI in ROIs:
                    
                    #Open the current ROI
                    current_ROI_directory = os.path.join(ROI_temp_directory, ROI)
                    rm.runCommand("Open", str(current_ROI_directory))
                    rm.select(0)
                    
                    #Duplicate the current ROI and get it into a variable
                    IJ.run("Duplicate...", "title=current_ROI.tif duplicate")
                    cropped_cell = IJ.getImage()
                    
                    #Make the directories and names to save the images
                    save_cropped_directory = os.path.join(cropped_cells_directory, raw_image_original_name)
                    save_cropped_name = os.path.join(save_cropped_directory, os.path.splitext(ROI)[0]+".jpg")					
                    if not os.path.exists(save_cropped_directory):
                        os.makedirs(save_cropped_directory)
                    
                    #Save cropped image, give it 1 second to finish, and close the cropped image and the ROI used to make it
                    IJ.saveAs(cropped_cell, "Jpeg", save_cropped_name)
                    cropped_cell.close()
                    rm.runCommand("Delete")
                    
            #Print a progress update
            print("Cropping of ROIs on image " + raw_image_name + " complete!")
            
            #Close the current raw image just completed, empty memory and proceed to the next image
            current_raw_image.close()
            IJ.run("Collect Garbage", "")
            
    #Close the ROI manager when we finish cropping all the images (for independency between sections)
    rm.close()
    
    #Print the time spent cropping
    partial_timer1 = datetime.now()
    cropping_time = (partial_timer1.getTime() - whole_script_starting_time.getTime())/1000.00
    print("Time spent cropping all the images (hours):", round(cropping_time/3600, 1))
    

######################################################################################################################################################################################
############################################################# PLA quantification (Measure cell area + puncta) ########################################################################

#This section quantifies area of the cell and number of puncta per cell by 2 methods: Analyze Particles and Find Maxima (Review results to see which works better for the experiment)
if Quantification!= "-":
    
    #This line is needed to avoid problems with measuring ROI area
    IJ.run("Set Measurements...", "area display redirect=None decimal=2")
    
    #Check if we have one pair of parameters or two for the quantification methods
    if ("," in particle_sizes) & ("," in particle_circularity):
        particle_sizes_T = particle_sizes.split(",")[0]
        particle_sizes_FM = particle_sizes.split(",")[1]
        particle_circularity_T = particle_circularity.split(", ")[0]
        particle_circularity_FM = particle_circularity.split(", ")[0]
    else:
        particle_sizes_T = particle_sizes_FM = particle_sizes
        particle_circularity_T = particle_circularity_FM = particle_circularity
    
    #Create neccesary directories
    analysis_directory = os.path.join(exp_condition_folder, "Quantification")
    if not os.path.exists(analysis_directory):
        os.makedirs(analysis_directory)
    analysis_ROIs_directory = os.path.join(ROIs_directory, "For Analysis")
    
    #Initialize the ROI manager and variables to save all the results table
    rm = RoiManager()
    maxima_ROI_names = []
    maxima_raw_image_names = []
    maxima_cell_areas = []
    maxima_cell_particle_count = []
    t_ROI_names = []
    t_raw_image_names = []
    t_cell_areas = []
    t_cell_particle_count = []
    
    #Walk through the raw image folder in case additional subfolders are used
    for raw_temp_directory, subfolder, raw_image_names in os.walk(raw_image_directory):
        raw_image_names.sort()
        
        #Iterate through each raw image 
        for raw_image_name in raw_image_names:
            
            #Since this version of the script works with Z-projected images, we need to trim the name of the images (MAX_Row_01_05.tif to find a folder Row_01_05)
            raw_image_original_name = raw_image_name.split("X_")[1]
            raw_image_original_name = raw_image_original_name.split(".t")[0]
            
            #Find the folder with the ROIs for the current raw image
            ROIs_to_analyze_folder = os.path.join(analysis_ROIs_directory, raw_image_original_name)
            
            #Now we're ready to open the current raw image 
            current_raw_image = IJ.openImage(os.path.join(raw_temp_directory, raw_image_name))
            while current_raw_image==None:
                time.sleep(0.5)
            current_raw_image.show()
            
            #Split the image and close channels not needed 
            IJ.run("Split Channels")
            for channel in [5, 4, 3, 2, 1]:
                channel_to_close = WindowManager.getImage("C"+str(channel)+"-"+raw_image_name)
                if (PLA_channel != channel) and (channel_to_close != None):
                    channel_to_close.close()
            
            #Subtract background (needed to enhance particle detection) and get the PLA channel into a variable
            IJ.run("Subtract Background...", "rolling="+str(PLA_background_radius))
            current_PLA_channel = IJ.getImage()
            
            #Based on the quantification method selected by the user, we may do or skip what is needed for the Find Maxima method 
            if (Quantification == "Find Maxima + Analyze Particles") or (Quantification == "Both"):
                
                #Create the appropriate folder to save this set of images
                cropped_cells_directory = os.path.join(summary_ppt_cells_directory, "FM_Particles")
            
                #Run the function Find Maxima with the parameter that the user gave and get the image to quantify the ROIs
                IJ.run("Find Maxima...", "prominence="+str(prominence)+" output=[Maxima Within Tolerance]")
                maxima_PLA_channel = IJ.getImage()
                maxima_PLA_channel.setTitle("Maxima.tif")
                IJ.selectWindow("Maxima.tif")
                
                #Walk through the ROIs folder to get all the ROIs
                for ROI_temp_directory, subfolder2, ROIs in os.walk(ROIs_to_analyze_folder):
                    ROIs.sort()
                    
                    #Iterate through each ROI (for the current opened image)
                    for ROI in ROIs:
                        
                        #Open the current ROI
                        current_ROI_directory = os.path.join(ROI_temp_directory, ROI)
                        rm.runCommand("Open", current_ROI_directory)
                        rm.select(0)
                        
                        #Quantify the variables of interest for the current ROI (adjust these parameters if needed)
                        IJ.run("Measure", "")
                        IJ.run("Analyze Particles...", "size="+particle_sizes_FM+" pixel circularity="+particle_circularity_FM+" show=[Overlay Masks] summarize")
                        
                        #Duplicate the current ROI and get it into a variable
                        IJ.run("Duplicate...", "title=current_ROI.tif duplicate")
                        cropped_cell = IJ.getImage()
                        rm.runCommand(cropped_cell,"Show None")
                        rm.runCommand(cropped_cell,"Show All without labels")
                        
                        #Make the directories and names to save the images
                        save_cropped_directory = os.path.join(cropped_cells_directory, raw_image_original_name)
                        save_cropped_name = os.path.join(save_cropped_directory, os.path.splitext(ROI)[0]+".jpg")					
                        if not os.path.exists(save_cropped_directory):
                            os.makedirs(save_cropped_directory)
                        
                        #Save cropped image, give it 1 second to finish, and close the cropped image and the ROI used to make it
                        IJ.saveAs(cropped_cell, "Jpeg", save_cropped_name)
                        time.sleep(0.5)
                        cropped_cell.close()
                        rm.runCommand("Delete")
                        
                        #Save the current ROI and raw image names for the results table
                        maxima_ROI_names.append(ROI)
                        maxima_raw_image_names.append(raw_image_name)
                        
                #Get the columns of interest from the Measure and Analyze Particles results tables
                maxima_areas_table = ResultsTable.getResultsTable("Results") 
                maxima_cell_areas = maxima_cell_areas + list(maxima_areas_table.getColumn("Area"))
                maxima_particles_table = ResultsTable.getResultsTable("Summary") 
                maxima_cell_particle_count = maxima_cell_particle_count + list(maxima_particles_table.getColumn("Count"))
                IJ.selectWindow("Results")
                IJ.run("Close")
                IJ.selectWindow("Summary")
                IJ.run("Close")
                
                #Close the current maxima image just completed and proceed to the next image
                maxima_PLA_channel.changes = False
                maxima_PLA_channel.close()
                IJ.run("Collect Garbage", "")
                
                #When we are doing the Find Maxima method only, we need to close the original image since it wont be used
                if Quantification == "Find Maxima + Analyze Particles":
                    current_PLA_channel.changes = False
                    current_PLA_channel.close()
                        
            #Based on the quantification method selected by the user, we may do or skip what is needed for the Threshold method 
            if (Quantification == "Threshold + Analyze Particles") or (Quantification == "Both"):
                
                #Create the appropriate folder to save this set of images
                cropped_cells_directory = os.path.join(summary_ppt_cells_directory, "T_Particles")
                
                #Threshold the image and run watershed
                IJ.setAutoThreshold(current_PLA_channel, threshold_method + " dark")
                IJ.run(current_PLA_channel, "Convert to Mask", "")
                IJ.run("Watershed")
                thresholded_PLA_channel = IJ.getImage()
            
                #Walk through the ROIs folder to get all the ROIs
                for ROI_temp_directory, subfolder2, ROIs in os.walk(ROIs_to_analyze_folder):
                    ROIs.sort()
                    
                    #Iterate through each ROI (for the current opened image)
                    for ROI in ROIs:
                        
                        #Open the current ROI
                        current_ROI_directory = os.path.join(ROI_temp_directory, ROI)
                        rm.runCommand("Open", current_ROI_directory)
                        rm.select(0)
                        
                        #Quantify the variables of interest for the current ROI (adjust these parameters if needed)
                        IJ.run("Measure", "")
                        IJ.run("Analyze Particles...", "size="+particle_sizes_T+" pixel circularity="+particle_circularity_T+" show=[Overlay Masks] summarize")
                        
                        #Duplicate the current ROI and get it into a variable
                        IJ.run("Duplicate...", "title=current_ROI.tif duplicate")
                        cropped_cell = IJ.getImage()
                        rm.runCommand(cropped_cell,"Show None")
                        rm.runCommand(cropped_cell,"Show All without labels")
                        
                        #Make the directories and names to save the images
                        save_cropped_directory = os.path.join(cropped_cells_directory, raw_image_original_name)
                        save_cropped_name = os.path.join(save_cropped_directory, os.path.splitext(ROI)[0]+".jpg")					
                        if not os.path.exists(save_cropped_directory):
                            os.makedirs(save_cropped_directory)
                        
                        #Save cropped image, give it 1 second to finish, and close the cropped image and the ROI used to make it
                        IJ.saveAs(cropped_cell, "Jpeg", save_cropped_name)
                        time.sleep(1)
                        cropped_cell.close()
                        rm.runCommand("Delete")
                        
                        #Save the current ROI and raw image names for the results table
                        t_ROI_names.append(ROI)
                        t_raw_image_names.append(raw_image_name)
                       
                #Get the columns of interest from the Measure and Analyze Particles results tables
                t_areas_table = ResultsTable.getResultsTable("Results") 
                t_cell_areas = t_cell_areas + list(t_areas_table.getColumn("Area"))
                t_particles_table = ResultsTable.getResultsTable("Summary") 
                t_cell_particle_count = t_cell_particle_count + list(t_particles_table.getColumn("Count"))
                IJ.selectWindow("Results")
                IJ.run("Close")
                IJ.selectWindow("Summary")
                IJ.run("Close")
                
                #Close the current raw image just completed (need to set changes as False since we dont want to save the thresholded image) and proceed to the next image
                thresholded_PLA_channel.changes = False
                thresholded_PLA_channel.close()
                IJ.run("Collect Garbage", "")
            
            #Print a progress update
            print("Quantification of ROIs on image " + raw_image_name + " complete!")
            
    #Close the ROI manager when we finish quantifying all the images 
    rm.close()

    #Finally, save the results table to a csv file
    if Quantification == "Threshold + Analyze Particles":
        rows = zip(t_raw_image_names, t_ROI_names, t_cell_particle_count, t_cell_areas)
        column_titles = ("Image used", "Cell quantified", "Particle count", "Cell area")
    elif Quantification == "Find Maxima + Analyze Particles":
        rows = zip(maxima_raw_image_names, maxima_ROI_names, maxima_cell_particle_count, maxima_cell_areas)
        column_titles = ("Image used", "Cell quantified", "Particle count", "Cell area")
    else :
        rows = zip(t_raw_image_names, t_ROI_names, t_cell_particle_count, t_cell_areas, maxima_cell_particle_count)
        column_titles = ("Image used", "Cell quantified", "Particle count threshold", "Cell area", "Particle count maxima")
    
    with open(os.path.join(analysis_directory, "Results.csv"), "wb") as results_file:
        writer = csv.writer(results_file)
        writer.writerow(column_titles)
        for row in rows:
            writer.writerow(row)
            
    #Print the time spent quantifying
    partial_timer2 = datetime.now()
    quantification_time = (partial_timer2.getTime() - whole_script_starting_time.getTime())/1000.00
    quantification_time = round(quantification_time/3600, 1) if Crop_cells==False else round(quantification_time/3600, 1) - round(cropping_time/3600, 1)
    print("Time spent cropping all the images (hours):", quantification_time)
    

######################################################################################################################################################################################

#Finish the MAIN timer and get the total number of seconds spent
whole_script_ending_time = datetime.now()
whole_script_running_time = (whole_script_ending_time.getTime() - whole_script_starting_time.getTime())/1000.00

#Print a summary of the work done and time it required
print("Whole script running time for one channel/condition (hours):", round(whole_script_running_time/3600, 1))

######################################################################################################################################################################################
######################################################################################################################################################################################
######################################################################################################################################################################################
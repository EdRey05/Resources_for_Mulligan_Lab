'''--------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------
--------------------------------------------------METADATA-------------------------------------------------

Description: Scripts to help quantify the colocalization of EEA1 and TMEM127 (WT, C140Y and S147del)
Experiment name: Exp1_TMEM127 coloc EEA1-LAMP2-TGN46 05 May 2019
Samples prepared by: Aisha N. Rekab [May 2019]
Images acquired by: Aisha N. Rekab and Eduardo Reyes-Alvarez [May 05th, 2019]


Experiment folder (lab server): ARekab/Microscopy/Exp1_TMEM127 coloc EEA1-LAMP2-TGN46 05 May 2019/
Images analyzed in subfolder: /Processed Images TMEM127-EEA1/
Results in subfolder: /Quantification/Analysis_Exp1_TMEM-EEA1_05May2022_colocalization_DH-ERA May 2022/


Scripts wrote by: Eduardo Reyes-Alvarez [May 2022] (both IJM and Python equivalent do the same)
Analysis done by: Dinah Heiligensetzer [May 2022]
Purpose of analysis: Use Aisha's unpublished data for Tim Walker's TMEM paper

How the scripts were used: The images from the indicated subfolder were open on ImageJ(Fiji) and the 
                           stacks were manually trimmed to remove slices out of focus. Then, the code
                           below for Step 2, 3 and 4 was run. Step 5 was to threshold the images, but 
                           the images showed inconsistencies so we manually tested different methods
                           from the Image->Adjust->Threshold dropdown menu for each channel and kept
                           record of the one selected (see excel file in the results folder indicated
                           above). After that, an ROI around the cell of interest was drawn and saved
                           with the same name as the original image (subfolder of ROIs in the results
                           folder). Then the Steps 6 and 7 were selected, run, and examined in case
                           adjustment of the parameters was needed (see Step 7) (parameters recorded
                           on the excel file). Once done, Step 8, 9 and 10 were run, the particle 
                           numbers saved to the excel file, and the Flatenned image was manually saved
                           with the same name as the original image (subfolder of Colocalized objects).
                           The results were processed in the same excel file by Eduardo, bad cells or
                           artifacts were removed, and the final numbers were graphed (see .pzfx file).

----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------'''

#------------------------------------------Import neccesary packages--------------------------------------#

import os
import time
from datetime import datetime
from ij import IJ, ImagePlus
from ij import WindowManager
from ij.plugin.frame import RoiManager
from ij.plugin import ImageCalculator
from ij.gui import Roi

#-------------------------------Step 1: Trim hyperstacks (manually)--------------------------------------#

#--------------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------#

#-----------------------Step 2: Prepare channels to use (Run steps 2,3 and 4 together)-------------------#

#Rename the opened image so it is easier to iterate
imp0 = IJ.getImage()
imp0.setTitle("Cell.tif")

#Split original image into different channels and close the Hoechst (C1) and RET (C2)
IJ.run("Split Channels")
IJ.selectWindow("C3-Cell.tif")
IJ.run("Close")


#------------------------Step 3: Z-project and make composite image (merge)------------------------------#

#Rename the channels, EEA1 for C4 (make red) and TMEM for C3. Make projection and rename too
IJ.selectWindow("C1-Cell.tif")
imp1 = IJ.getImage()
imp1.setTitle("EEA1.tif")
IJ.run("Channels Tool...")
IJ.run("Red")
IJ.run("Z Project...", "projection=[Max Intensity]")
imp1_1 = IJ.getImage()
imp1_1.setTitle("Projection_EEA1.tif")

IJ.selectWindow("C2-Cell.tif")
imp2 = IJ.getImage()
imp2.setTitle("TMEM.tif")
IJ.run("Z Project...", "projection=[Max Intensity]")
imp2_1 = IJ.getImage()
imp2_1.setTitle("Projection_TMEM.tif")

#Close original images (z-stacks) as we will process the projection only
imp1.close()
imp2.close()


#Make composite image (will be used at the end for validation of the colocalized objects)
IJ.run("Merge Channels...", "c1=Projection_EEA1.tif c2=Projection_TMEM.tif create keep")


#--------------Step 4: Duplicate images to threshold one and keep the other as a backup------------------#

IJ.selectWindow("Projection_EEA1.tif")
IJ.run("Duplicate...", "title=Thresholded_EEA1.tif")
IJ.selectWindow("Projection_TMEM.tif")
IJ.run("Duplicate...", "title=Thresholded_TMEM.tif")


#--------------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------#


#-----Step 5: Threshold TMEM and EEA1 channels (manually), make an ROI around the cell and save it-------#

#Select the ROI in both channels before proceeding 

#--------------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------#


#----Step 6: Run Watershed and Fill holes to improve results from Analyze Particles (Run step 6 and 7)---#

IJ.selectWindow("Thresholded_TMEM.tif")
IJ.run("Watershed")
IJ.run("Fill Holes")

IJ.selectWindow("Thresholded_EEA1.tif")
IJ.run("Watershed")
IJ.run("Fill Holes")


#------------------------Step 7: Run Analyze Particles for both channels---------------------------------#

#Run it this way first, examine the resulting image with coloured objects
#If the numbers give an inappropriate result, edit the size, and re-run this step only
#Once the objects obtained look good, write down the number displayed in the results window

IJ.selectWindow("Thresholded_TMEM.tif")
IJ.run("Analyze Particles...", "size=10-Infinity pixel circularity=0.01-1.00 show=Overlay summarize")

IJ.selectWindow("Thresholded_EEA1.tif")
IJ.run("Analyze Particles...", "size=20-Infinity pixel circularity=0.01-1.00 show=Overlay summarize")


#--------------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------#

#---------------------Manual inspection of images required before proceeding-----------------------------#

#--------------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------#

#--Step 8: Run the Image Calculator to determine the intersection between objects (Run step 8,9 and 10)--#

IJ.selectWindow("Thresholded_EEA1.tif")
imp1 = IJ.getImage()
IJ.selectWindow("Thresholded_TMEM.tif")
imp2 = IJ.getImage()
imp3 = ImageCalculator.run(imp1, imp2, "AND create")
imp3.show()


#-------------------Step 9: Quantify the objects that intersected between the channels-------------------#

#Write down the number displayed in the results window

IJ.selectWindow("Result of Thresholded_EEA1.tif")
rm = RoiManager.getRoiManager()
rm.select(0)
IJ.run("Analyze Particles...", "size=20-Infinity pixel circularity=0.01-1.00 show=Overlay summarize add")


#----------Step 10: Generate a flattened image between the composite and overlapping objects-------------#

#The final image needs to be manually saved
#Use this image to validate that the objects with white lines show some degree of yellow

IJ.selectWindow("Composite")
imp = IJ.getImage()
rm.runCommand(imp,"Show None")
rm.runCommand(imp,"Show All")
rm.runCommand(imp,"Show All without labels")
rm.setGroup(0)
rm.setPosition(0)
rm.runCommand("Set Color", "white")
IJ.run("Flatten")
imp = IJ.getImage()
imp.setTitle("Flattened")

#Close some of the windows no longer needed
IJ.selectWindow("Composite")
IJ.run("Close");
IJ.selectWindow("Result of Thresholded_EEA1.tif")
IJ.run("Close");
IJ.selectWindow("Thresholded_TMEM.tif")
IJ.run("Close")
IJ.selectWindow("Projection_TMEM.tif")
IJ.run("Close")
IJ.selectWindow("Thresholded_EEA1.tif")
IJ.run("Close")
IJ.selectWindow("Projection_EEA1.tif")
IJ.run("Close")
rm.close()



#---------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------#

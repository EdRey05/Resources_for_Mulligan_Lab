# Resources for the Mulligan Lab

Scripts made by Eduardo Reyes Alvarez (Ph.D.) to help in data processing and analysis of several experiments carried out in Dr. Lois Mulligan's Lab at Queen's University. 

Most of the tools developed (scripts/notebooks) are described below, and include a preview + a link to their folder (click on the blue title). ***For a more detailed video tutorial check:*** [Tutorials](https://github.com/EdRey05/Resources_for_Mulligan_Lab/tree/main/Tutorials).


# [Merger of images into hyperstacks](https://github.com/EdRey05/Resources_for_Mulligan_Lab/tree/main/Tools%20for%20EVOS-M7000%20images)

**Context:**

The EVOS M7000 imager takes pictures of a field of view (FOV) at different heights (Z-slices) and in different colours (channel blue, green, red...). However, it does not save the pictures as hyperstacks (a single file containing all slices and colours for each FOV). Instead, the equipment separately saves each slice for each colour, resulting in 5, 20 or more TIF files from the same FOV and in grayscale. We can put the images back together using the ImageJ software, since we do image analysis with it and it can run macros/scripts in languages including Jython (Python implementation to run in Java).

**Problems:**
* Opening, stacking and merging into hyperstacks is simple in  ImageJ, but not manually feasible for more than a few dozens of images. Some of my experiments had 4-6 thousand TIFs.
* The images are saved with a name that makes complicated to manually identify the ones that go together: ***ExperimentName_Bottom Slide_R_p00_z00_0_A01f00d0.tif***

**Solution:**
* I analyzed and figured out the parts of the image names that indicate which correspond to the same FOV: z00 indicates the slices, A01 indicates the area/location, f00 indicates the FOV, and d0 indicates the colour.
* I made a script using the `os` Python library to scan all the files of a folder, get the image names and extract the relevant information with string and path operations. Then I applied a special sorting to cluster together all TIFs of the same FOV.
* I automated the merging of TIFs into hyperstacks using the modules `IJ` and `ImagePlus` from the `ij` library. This required logic controls to identify when to stack slices, when to merge all stacks into a composite, and when to save the hyperstack.

**Preview of the script:**
![](Tutorials/Preview_Images_to_Hyperstacks_merger.gif)


# [Tools to handle ROIs during PLA quantification](https://github.com/EdRey05/Resources_for_Mulligan_Lab/tree/main/Tools%20for%20PLA%20quantification)

**Context:**

In Proximity Ligation Assays (PLA) we quantify the number of red puncta/dots in blue+green+red images, which reflects the interactions of two proteins. We make a region of interest (ROI) around individual cells to quantify the interactions per cell, and make a bigger ROI for representative figures or data presentation. In my PLA experiments, I quantified around 10,000 individual cells using the ImageJ software and generated multiple tools described below to automate the saving and opening of ROIs.

**Problems:**
* Drawing the ROIs has to be done manually due to the selection criteria of the experimenter, however, saving them is time-consuming and does not require expertise.
* Since the two ROIs refer to the same cell, we need a strategy to keep a name and indexing number for tracking purposes.
* The experimenter should pick the cells of interest and at least draw one set of the ROIs, but can be helped by other people drawing the pre-selected ROIs

**Solution:**
* I implemented a Jython script using the `Roi` and `RoiManager` modules from the `ij` library to get the content of the ROI manager into a variable I can iterate through. 
* With this variable, I can get any number of pairs of ROIs drawn by the user for each cell but they must be in order: first one with the rectangle tool that will be saved in a "For Presentation" folder, and secondly one with the polygon tool that will be saved in a "For Analysis" folder.
* During the iteration, all the even-numbered ROIs (rectangles) are renamed from 0, 2, 4... to index/2 +1 = 1, 2, 3... and saved as "1_2.roi" in the folder mentioned above. All the odd-numbered ROIs (polygons) are renamed from 1, 3, 5... to (index+1)/2 = 1, 2, 3... and saved as "1_1.roi" in the corresponding folder.
* Additionally, a jpg preview of the cells selected is made (just showing the rectangles) for quick data validation/exploration.

## Tool 01
**Description:**
This tool saves in a temporary folder the two sets of ROIs as described above. It has no requirements other than an opened image with all the ROIs added to the manager, but the products have to be manually moved to their appriopriate destination before doing the next image.

**Preview of the script:**
![Preview_Tool_01_ROI_saving_for_PLA](https://user-images.githubusercontent.com/62916582/203685126-e7668b9e-dbac-425e-b59c-43440aa1df3a.gif)



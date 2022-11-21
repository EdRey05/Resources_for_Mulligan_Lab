# Resources for the Mulligan Lab

Scripts made by Eduardo Reyes Alvarez (Ph.D.) to help in data processing and analysis of several experiments carried out in Dr. Lois Mulligan's Lab at Queen's University. 

Most of the tools developed (scripts/notebooks) are described below, and include a preview + a link to the code (click on the blue title). For a more detailed video tutorial check the [Tutorials](https://github.com/EdRey05/Resources_for_Mulligan_Lab/tree/main/Tutorials).


# [Images to hyperstacks merger](https://github.com/EdRey05/Resources_for_Mulligan_Lab/tree/main/Tools%20for%20EVOS-M7000%20images)

**Context:**

The EVOS M7000 imager takes pictures of a field of view (FOV) at different heights (Z-slices) and in different colours (channel blue, green, red...). However, it does not save the pictures as hyperstacks (a single file containing all slices and colours for each FOV). Instead, the equipment separately saves each slice for each colour, resulting in 5, 20 or more TIF files from the same FOV and in grayscale. We can put the images back together using the ImageJ software, since we do image analysis with it and it can run macros/scripts in languages including Jython (Python implementation to run in Java).


**Problem:**
* Opening, stacking and merging into hyperstacks is simple in  ImageJ, but not manually feasible for more than a few dozens of images. Some of my experiments had 4-6 thousand TIFs.
* The images are saved with a name that makes complicated to manually identify the ones that go together: ***ExperimentName_Bottom Slide_R_p00_z00_0_A01f00d0.tif***


**Solution:**
* I analyzed and figured out the parts of the image names that indicate which correspond to the same FOV: z00 indicates the slices, A01 indicates the area/location, f00 indicates the FOV, and d0 indicates the colour.
* I made a script using the `os` Python library to scan all the files of a folder, get the image names and extract the relevant information with string and path operations. Then I applied a special sorting to cluster together all TIFs of the same FOV.
* I automated the merging of TIFs into hyperstacks using the libraries `IJ` and `ImagePlus`. This required logic controls to identify when to stack slices, when to merge all stacks into a composite, and when to save the hyperstack.

**Preview of the script:**
![](Tutorials/Preview_Images_to_Hyperstacks_merger.gif)





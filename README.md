{::options parse_block_html="true" /}
# Resources for the Mulligan Lab

Most of the tools developed are described below, and include a GIF preview + a link to the script/notebook (click on the title). The majority of these tools were designed to run within the **ImageJ/Fiji** software, which our lab commonly uses for data analysis, plus some notebooks made in **Google Colab** for additional tasks. These tools do not require any programming experience nor installing any other program (other than ImageJ) to be used.

***For more information on how to use the scripts, check:*** [Tutorials](https://github.com/EdRey05/Resources_for_Mulligan_Lab/tree/main/Tutorials).

***NOTE:*** If you are reading this on Github, check out the [Github page](https://edrey05.github.io/Resources_for_Mulligan_Lab/) for easier visualization. If you are already in the Github page (has colours), you can click on the button "View on Github" from the left box to access the main repository. 

# [Merger of images into hyperstacks](https://github.com/EdRey05/Resources_for_Mulligan_Lab/blob/main/Tools%20for%20EVOS-M7000%20images/Images_to_Hyperstacks_merger.py)

<details><summary markdown="span">READ MORE...</summary>

**Context:**

The **EVOS M7000** imager takes pictures of a field of view (FOV) at different heights (Z-slices) and in different colours (channel blue, green, red...). However, it does not save the pictures as hyperstacks (a single file containing all slices and colours for each FOV). Instead, the equipment separately saves each slice for each colour, resulting in 5, 20 or more TIF files from the same FOV and in grayscale. We can put the images back together using the ***ImageJ*** software, since we do image analysis with it and it can run macros/scripts in languages including ***Jython*** (Python implementation to run in Java).

**Problems:**
* Opening, stacking and merging into hyperstacks is simple in ***ImageJ***, but not manually feasible for more than a few dozens of images. Some of my experiments had 4-6 thousand TIFs.
* The images are saved with a name that makes complicated to manually identify the ones that go together: ***ExperimentName_Bottom Slide_R_p00_z00_0_A01f00d0.tif***

**Solution:**
* I analyzed and figured out the parts of the image names that indicate which correspond to the same FOV: z00 indicates the slices, A01 indicates the area/location, f00 indicates the FOV, and d0 indicates the colour.
* I made a script using the `os` ***Python*** library to scan all the files of a folder, get the image names and extract the relevant information with string and path operations. Then I applied a special sorting to cluster together all TIFs of the same FOV.
* I automated the merging of TIFs into hyperstacks using the modules `IJ` and `ImagePlus` from the `ij` library. This required logic controls to identify when to stack slices, when to merge all stacks into a composite, and when to save the hyperstack.

</details>
 
  
**Preview of the script:**
![](Tutorials/Preview_Images_to_Hyperstacks_merger.gif)


# Tools to handle ROIs during PLA quantification

<details><summary markdown="span">READ MORE...</summary>

**Context:**
  
In Proximity Ligation Assays (PLA) we quantify the number of red puncta/dots in blue+green+red images, which reflects the interactions of two proteins. We make a region of interest (**ROI**) around individual cells to quantify the interactions per cell, and make a bigger ROI for representative figures or data presentation. In   my PLA experiments, I quantified around 10,000 individual cells using the ImageJ software and generated multiple tools described below to automate the saving and       opening of ROIs.

**Problems:**
* Drawing the ROIs has to be done manually due to the selection criteria of the experimenter, however, saving them is time-consuming and does not require expertise.
* Since the two ROIs refer to the same cell, we need a strategy to keep a name and indexing number for tracking purposes.
* The experimenter should pick the cells of interest and at least draw one set of the ROIs, but can be helped by other people drawing the pre-selected ROIs

**Solution:**
* I implemented a ***Jython*** script using the `Roi` and `RoiManager` modules from the `ij` library to get the content of the ROI manager into a variable I can iterate through. 
* With this variable, I can get any number of pairs of ROIs drawn by the user for each cell but they must be in order: first one with the rectangle tool that will be saved in a "For Presentation" folder, and secondly one with the polygon tool that will be saved in a "For Analysis" folder.
* During the iteration, all the even-numbered ROIs (rectangles) are renamed from 0, 2, 4... to index/2 +1 = 1, 2, 3... and saved as "1_2.roi" in the folder mentioned above. All the odd-numbered ROIs (polygons) are renamed from 1, 3, 5... to (index+1)/2 = 1, 2, 3... and saved as "1_1.roi" in the corresponding folder.
* Additionally, a jpg preview of the cells selected is made (just showing the rectangles) for quick data validation/exploration.

</details>

## [Tool 01](https://github.com/EdRey05/Resources_for_Mulligan_Lab/blob/main/Tools%20for%20PLA%20quantification/Tool_01_ROI_saving_for_PLA.py)
**Description:**
This tool saves in a temporary folder the two sets of ROIs as described above. It has no requirements other than an opened image with all the ROIs added to the manager, but the products have to be manually moved to their appropriate destination before doing the next image.

**Preview of the script:**
![Preview_Tool_01_ROI_saving_for_PLA](https://user-images.githubusercontent.com/62916582/203685126-e7668b9e-dbac-425e-b59c-43440aa1df3a.gif)

## [Tool 02](https://github.com/EdRey05/Resources_for_Mulligan_Lab/blob/main/Tools%20for%20PLA%20quantification/Tool_02_ROI_saving_for_PLA.py)
**Description:**
This tool is split in two sections, the top part is for making the rectangular ROIs and the jpg preview (as mentioned in Tool 01), and the second part is for making the ROIs with the polygon tool. The idea behind the split parts is that the experimenter can pre-select the cells they want analyzed by doing the rectangular ROIs, and then someone else can take the jpg images to make the polygons, which is the time-consuming step.

**Preview of the script:**
![Preview_Tool_02_ROI_saving_for_PLA](https://user-images.githubusercontent.com/62916582/204342846-399fb3aa-db35-4cfe-a2e5-2f550d1314f6.gif)

## [Tool 03](https://github.com/EdRey05/Resources_for_Mulligan_Lab/blob/main/Tools%20for%20PLA%20quantification/Tool_03_ROI_opening_for_PLA.py)
**Description:**
This tool opens the two sets of ROIs that were drawn for an image. It has no requirements other than having a folder structure as described above (Processed..., ROIs). By openning a processed image (MAX projection TIF), the script can load the ROIs in case it is needed to review, delete, or add more ROIs (then just run tool 01).

**Preview of the script:**
![Preview_Tool_03_ROI_opening_for_PLA](https://user-images.githubusercontent.com/62916582/203877499-e528d699-5d2c-4cc5-9dbe-c07cd1293e3f.gif)


# [PLA quantification](https://github.com/EdRey05/Resources_for_Mulligan_Lab/blob/main/Tools%20for%20PLA%20quantification/PLA_quantification.py)

<details><summary markdown="span">READ MORE...</summary>

**Context:**

We quantify the PLA interactions (red dots) in our images using the ***ImageJ*** software and the regions of interest (**ROIs**) generated with the tools described above. For my experiments, I wanted to test two ways of quantifying the objects in my images: **1)** Applying a threshold method from the ***ImageJ*** tools (*Image-   ->Adjust-->Threshold*) or **2)** Using the ***Find Maxima*** tool on ***ImageJ*** (*Process-->Find Maxima*). Both methods are followed by object counting with the     ***Analyze Particles*** tool on ***ImageJ*** (*Analyze-->Analyze Particles*), and I wanted to also measure the area of the cells in case normalization was required (*Analyze-->Measure*).

**Problems:**
* The quantification process is tedious and time-consuming even for a single ROI (I ended up having ~10,000).
* We need to do the one quantification method first, capture the results that are given in a pop-up table, then do the other method (otherwise both get printed in the same table).
* The Measure tool for the area of the cells gives a different pop-up table, so we need to capture the data from there too and combine with the particle count.
* We need to get in one interactive menu all the input parameters needed to run 4 ***ImageJ*** tools which have their own interactive menu.
* We not only want numbers as outputs, but also, some images of the cells quantified and the objects counted so we can assess quality of the results and track any possible issues.

**Solution:**
* I implemented a ***Jython*** script using similar modules from the `ij` library as the tools to handle ROIs (see above), additionally, I implemented the module `ResultsTable` which was very important to handle the pop-up windows with the results.
* I made an interactive menu with the essential input parameters from all 4 tools used.
* The script gives a single .csv file with all the results combined in a table, and also saves .jpg images showing how the cells look and how the object detection worked (particles counted are couloured, black pixels were not counted).
* Opening the ROIs for an image, cropping them, doing the measurements and saving the results gets very fast using the script compared to manual clicking.

</details>
 
  
**Preview of the script:**
![Preview_PLA_quantification](https://user-images.githubusercontent.com/62916582/204093397-3830acbe-80a2-4660-9b64-f3a0445ae6d0.gif)


# [Automated PowerPoint for PLA results](https://github.com/EdRey05/Resources_for_Mulligan_Lab/blob/main/Tools%20for%20students/Eduardo%20Reyes/05-Design01_PLA_results_PPTX_generator%5BColab%5D.ipynb)

<details><summary markdown="span">READ MORE...</summary>

**Context:**

Once I've used the script shown above to quantify the Proximity Ligation Assay (**PLA**) puncta, I wanted to put the cropped images and results into a PowerPoint presentation to visualize easily and quickly the 100-500 cells I quantified per condition (total ~10,000). I also wanted to have two presentations with both quantification methods tested (see script above) to determine which was more appropriate for my experiments.

**Problems:**
* Manually copying, pasting, resizing, arranging and labeling all the images is incredibly time consuming and error-prone.
* ***ImageJ*** is not fully compatible with **Python** 3 and has its own version of it, so I can't install more libraries and things like `Pandas` and `Numpy` do not work there.

**Solution:**
* I found the package/library `python-pptx` which has been recently developed (functionalities limited but expanding) and allows for the creation of PowerPoint presentations from **Python** code.
* I dove in the documentation and was able to write a function to generate slides that look like this ***(open [the notebook](https://github.com/EdRey05/Resources_for_Mulligan_Lab/blob/main/Tools%20for%20students/Eduardo%20Reyes/05-Design01_PLA_results_PPTX_generator%5BColab%5D.ipynb) to read more details about my design parameters!!!)***:
![Slide_design](https://user-images.githubusercontent.com/62916582/204416858-70e0a772-ce0c-460a-a0b9-d3e6fddbd753.jpg)
* I passed to this function all my images and the quantification results so I can back-track cells with ROIs and their respective counts of dots.
* I set up a fully functional notebook on **Google Colab** for easy sharing with other lab members who don't need programming experience or install anything to use it. Also, it runs fast on that server (less than 5min to make ~100 slides with ~700 cells). 

</details>
 
  
**Preview of the script:**
![Preview_05-Design01_PLA_results_PPTX_generator Colab](https://user-images.githubusercontent.com/62916582/204415085-cc39bb7c-904e-487c-a16d-0d894c1e3249.gif)


# [Extracting RNASeq data from the Cancer Cell Line Encyclopedia](https://github.com/EdRey05/Resources_for_Mulligan_Lab/blob/main/Tools%20for%20students/Eduardo%20Reyes/03-ExtractCells_Broad_Institute_CCLE_2019_%5BColab%5D.ipynb)

<details><summary markdown="span">READ MORE...</summary>

**Context:**

The **Broad Institute** and **Novartis** published in 2019 huge datasets resulting from a collaboration to make available distinct measurements (RNA, metabolites, mutations, etc.) of a panel of over 1500 human cancer cell lines. In our lab, (Mulligan) we have multiple cancer cell lines for which we wanted to get the RNASeq data to do some exploratory studies looking for insights on the expression levels of specific proteins. The data can be found either in [cBioPortal for Cancer Genomics](https://www.cbioportal.org/) or directly from the [CCLE](https://sites.broadinstitute.org/ccle/) website.

**Problems:**
* The dataset useful to our needs is huge, containing thousands of rows by thousands of columns. We want to retrieve a few columns since we have less than 50 cancer cell lines in our lab.
* For few other applications, we may want to search for cell lines we don't have (or explore what's available), so we need to keep the original dataset.

**Solution:**
* I set up a **Google** account for our lab, which I used to upload the files for RNASeq (.txt files, ~500 mb each) to **Google Drive**.
* I made a short tool in **Google Colab**, which connects to the lab drive and retrieves the files to avoid having to download and upload 1gb frequently.
* I used `pandas` dataframe operations and user inputs to make a search tool, and extract only the required columns (all genes/rows) into a .csv file.
* **Note:** The notebook requires specific folder structure and files to run ([see notebook](https://github.com/EdRey05/Resources_for_Mulligan_Lab/blob/main/Tools%20for%20students/Eduardo%20Reyes/03-ExtractCells_Broad_Institute_CCLE_2019_%5BColab%5D.ipynb)). Users not logged into the lab account may need to edit the directories and get the files to replicate the preview/tutorial. 

</details>
 
  
**Preview of the script:**
![Preview_03-ExtractCells_Broad_Institute_CCLE_2019_ Colab](https://user-images.githubusercontent.com/62916582/204422004-47fe5726-d92d-4193-bc6a-ea30b3a93cc1.gif)


# [Kaplan-Meier survival plot generator](https://github.com/EdRey05/Resources_for_Mulligan_Lab/blob/main/Tools%20for%20students/Eduardo%20Reyes/01-METABRIC_KM_Plot_First_Batch_%5BColab%5D.ipynb)

<details><summary markdown="span">READ MORE...</summary>

**Context:**

A short project looking at breast cancer data available in the [cBioPortal for Cancer Genomics](https://www.cbioportal.org/) server was carried out. The study used the [METABRIC](https://www.cbioportal.org/study/summary?id=brca_metabric) dataset published in Nature journals (2012 and 2016) which has just over 2500 tumour samples. The aim of the project was to evaluate survival of patients through **Kaplan-Meier (KM)** plots and correlate them with expression levels of pairs of proteins (the **RET** receptor + ~50 hints we got from ***synthetic lethality*** assays). Our hypothesis was that the survival of a patient should increase when RET and any other of the hints were expressed at low levels in the patient, partially mimicking the concept of synthetic lethality (less expression of the pair of proteins --> tumour cells die or not proliferate as much --> the patient lives longer).

**Problems:**
* We have huge datasets for clinical and RNASeq data in .txt files which we need to clean, merge and filter.
* We want to make **KM** plots for subsets of patients based on expression levels: Low RET + Low other, Low RET + High other, High RET + Low other, and High RET + High other (4 survival curves plotted together per pair of RET + other protein).

**Solution:**
* I set up a **Google** account for our lab, which I used to upload the files for clinical and RNASeq data (.txt files, ~500 mb each) to **Google Drive**.
* I made two notebooks in **Google Colab**, which connect to the lab drive and retrieves the files to avoid having to download and upload 1gb frequently.
* I generated a [first batch](https://github.com/EdRey05/Resources_for_Mulligan_Lab/blob/main/Tools%20for%20students/Eduardo%20Reyes/01-METABRIC_KM_Plot_First_Batch_%5BColab%5D.ipynb) and a [second batch](https://github.com/EdRey05/Resources_for_Mulligan_Lab/blob/main/Tools%20for%20students/Eduardo%20Reyes/02-METABRIC_KM_Plot_Second_Batch_%5BColab%5D.ipynb) of **KM** plots using the `KaplanMeierFitter` module from the `lifelines` library, also retrieving key data like time to 50% survival for all subgroups.
* I used diverse data cleaning and filtering steps (see notebooks) to make the intended subgroups and combine the clinical and RNASeq data. 
* From all the pairs we evaluated, most showed no significant differences between subgroups, however, we got a small group of very interesting findings that match our hypothesis and will be followed up in other projects. This is an example of the RET-SPEG very promising **KM** plot:
![RET-SPEG](https://user-images.githubusercontent.com/62916582/204429130-1c836469-198b-4d8a-bc2c-67b8de0faaff.png)

</details>
 
  
**Preview of the script:**
![Preview_01-02-METABRIC_KM_Plot Colab](https://user-images.githubusercontent.com/62916582/204424020-bae3613c-bf10-4a3b-9d50-beaf50ca8eee.gif)

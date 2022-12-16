#This script segments nuclei and spots from multi-dimensional images in DeltaVision format.
#It calculates the number of nuclei and spots in each image stack and saves the result as a table. It also 
#saves nuclei and spot segmentation images as a control. This script was developed in the frame of a project
#with Julia Bruggisser, VetSuisse, Bern University
#
#The saved table has the following columns:
# Experiment: folder name of the experiment to which the image belongs
# Experiment index: an index common to all images of a given experiment (it has no specific meaning,
#	its just the order in which experiments are analyzed. Useful to group data for plotting.
# File name: name of the image
# Number of nuclei: number of detected nuclei
# Number of spots: number of detected spots
#
#Guillaume Witz, Scientific IT Support, Bern University, guillaume.witz@math.unibe.ch
#01.05.2019

from ij import IJ, ImagePlus, WindowManager
from ij.plugin import ChannelSplitter, ZProjector, Thresholder
from ij.io import OpenDialog, DirectoryChooser

from ij.measure import ResultsTable
from ij.plugin.filter import ParticleAnalyzer
import os, time, glob, sys

#ask for main directory
dc = DirectoryChooser('Pick main data directory')

#find all sub-directories that should correspond to separate experiments
exp_dirs = glob.glob(dc.getDirectory()+'*')
exp_dirs = [x for x in exp_dirs if os.path.isdir(x)]

#my_results is a table that collects results. It contains the file name, # of nuclei, # of spots
my_results = ResultsTable()

global_index = 0 
for exp_ind, e in enumerate(exp_dirs):

	#find all images within a folder
	files = glob.glob(e+'/*.dv')

	#analyze all images
	for ind,f in enumerate(files):
		print(f)
		
		#open file using bioformats
		IJ.run("Bio-Formats", 'open='+f+' color_mode=Default rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT');
		
		#change stack name to current_image and split channels (named C1-, C2-)
		imp = IJ.getImage()
		imp.setTitle("current_image");
		IJ.run("Split Channels");
	
		#///////// Nuclei segmentation ////////////
		
		#select nuclei image
		nuclei_name = 'C1-current_image'
		IJ.selectWindow(nuclei_name)
		imp = IJ.getImage()
		
		#maximum projection
		imp = ZProjector.run(imp,"max");
		imp.show()
		
		#thresholding using minimum method, invert and apply closing operation
		IJ.setAutoThreshold(imp, "Minimum dark");
		ip = Thresholder().createMask(imp)
		imp2 = ImagePlus('Result',ip)
		IJ.run(imp2, "Invert", "");
		IJ.run(imp2, "Morphological Filters", "operation=Closing element=Disk radius=5");
	
		#Use binary watershed (based on EDT) to segment mask
		IJ.selectWindow('Result-Closing')
		imp = IJ.getImage() 
		IJ.run(imp, "Watershed", "");
	
		#do particle analysis (this is only created to count objects, but could be used to gather infos
		new_table = ResultsTable()
		pa = ParticleAnalyzer(ParticleAnalyzer.SHOW_OUTLINES, ParticleAnalyzer.AREA, new_table, 100, 10000000)
		pa.analyze(imp);

		imp = IJ.getImage()
		IJ.saveAs(imp, "Jpeg", f.split('.')[0]+'_seg.jpg');
		
		new_table.show("Nuclei"); 
		
		#fill results table with file name and number of nuclei
		my_results.setValue('Experiment', global_index, os.path.basename(e))
		my_results.setValue('Experiment index', global_index, exp_ind)
		my_results.setValue('File name', global_index, os.path.basename(f))
		my_results.setValue('Number of nuclei', global_index, new_table.size())


		#//////// Spot segmentation /////////////

		#get spot image and wait for 1s. Without the wait, the next operation is done on the wrong image...
		new_name = 'C2-current_image'
		IJ.selectWindow(new_name)
		imp = IJ.getImage()

		time.sleep(1)
	
		#Filter image using 3D LoG filter
		IJ.run("LoG 3D", "sigmax=1.5 sigmay=1.5 sigmaz=3 displaykernel=0 volume=1");
		
		#wait until the filtering is done (apparently fiji scripts don't wait on plugins to be done)
		imp = IJ.getImage()
		imagesName = imp.getTitle()
		
		while imagesName != "LoG of "+new_name:
			imp = IJ.getImage()
			imagesName = imp.getTitle()
	
		#transform image to 16bit and use an arbitrary threshold to select spots (based on image with many spots)
		IJ.selectWindow("LoG of "+new_name); 
		imp = IJ.getImage()
		IJ.run("16-bit");
		IJ.setThreshold(imp, 0, 20000);
		IJ.run(imp, "Make Binary", "method=Default background=Light");
	
		#do 3D particle analysis
		IJ.run(imp, "3D Objects Counter", "threshold=115 slice=36 min.=10 max.=76546048 exclude_objects_on_edges objects statistics summary");

		#get reference to 3D particles analysis window
		rt = WindowManager.getWindow('Statistics for LoG of C2-current_image').getTextPanel().getResultsTable()
		
		
		#complete the results table with # of spots
		my_results.setValue('Number of spots', global_index, rt.size())

		
		#project to store image
		IJ.selectWindow('Objects map of LoG of C2-current_image');
		imp = IJ.getImage();
		imp = ZProjector.run(imp,"max");
		IJ.run(imp, "glasbey on dark", "");
		imp.setDisplayRange(0, int(rt.size()))
		imp.updateImage()
		IJ.saveAs(imp, "Jpeg", f.split('.')[0]+'_spots.jpg');

		#sys.exit("Error message")
		
		
		
		#update global index to switch lines in the results table
		global_index+=1

		#close all images that are open
		while WindowManager.getCurrentImage() is not None:
			img = WindowManager.getCurrentImage()
			img.changes = False
			img.close();

#save the results file in the main data folder
my_results.show('FileSummary')
IJ.saveAs("Results", dc.getDirectory()+'FileSummary.csv');


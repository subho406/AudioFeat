#!/usr/bin/python
'''extractFeatures.py
	
Script for generating audio features given 
a directory and appending output to a csv
file.


'''

from libs import processAudio as pa


__version__ = '0.1'
__author__ = 'Subhojeet Pramanik'


import os
import argparse
import pandas as pd


exts=['.mp3','.wav']



def get_filepaths(directory):
    """
    This function will generate the file names in a directory 
    tree by walking the tree either top-down or bottom-up. For each 
    directory in the tree rooted at directory top (including top itself), 
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.

    return file_paths  # Self-explanatory.


def get_audio_files(filelist):
	'''Get the list of audio files from a list of 
		all files.

		Arguments:
			filelist	- 	Tuple containing the list of audio file paths

		Returns:	pandas.DataFrame

	'''
	audio_list=[]
	for f in filelist:
		filename, file_extension = os.path.splitext(f)
		if(file_extension in exts):
			audio_list.append(f)
	return audio_list



if __name__ == '__main__': 
	# Process Arguments
	parser = argparse.ArgumentParser(description='A script to extract content based features from audio files in a directory.')
	parser.add_argument('-d','--directory', help='Input directory containing audio files.',required=True)
	parser.add_argument('-o','--output',help='Output csv file', required=True)
	parser.add_argument('-j','--jobs',help='Number of jobs to run. Default: 1',required=False)
	parser.add_argument('-p','--progress',help='Show progress. Options: (yes, no), Default: yes',required=False)
	args = parser.parse_args()
	path=args.directory
	output=args.output
	jobs=args.jobs
	progress=args.progress

	# Get jobs value
	if(jobs!=None):
		jobs=int(args.jobs)
	else:
		jobs=1

	# Get progress value
	if(progress!=None):
		if(progress=='no'):
			progress=False
		else:
			progress=True
	else:
		progress=True

	# Start processing the audio files
	if(os.path.isdir(path)):
		audio_list=get_audio_files(get_filepaths(path))
		if(len(audio_list)>=1):
			print('Found the following audio files: '+str(audio_list))
			## Get all the Dataframes
			all_df=pa.process_audios(audio_list,jobs,progress)

			#Start writing the Dataframe to csv
			if(os.path.isfile(output)):				## If csv already exists append to it			
				for df in all_df:
					with open(output, 'a') as f:
						df.to_csv(f, header=False, index=False)
			else:									## Else create a new csv with header
				with open(output, 'w') as f:
					all_df[0].to_csv(f, header=True, index=False)
				for df in all_df[1:]:
					with open(output, 'a') as f:
						df.to_csv(f, header=False, index=False)				
		else:
			print('No audio files found. Exiting!')
	else:
		raise ValueError('Invalid arguments specified. The specified directory is not valid.')

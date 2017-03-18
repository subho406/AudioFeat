'''extractFeatures.py
	
Script for generating audio features given 
a directory and appending output to a csv
file.


'''


import os
from libs import processAudio as pa


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
	'''
	audio_list=[]
	for f in filelist:
		filename, file_extension = os.path.splitext(f)
		if(file_extension in exts):
			audio_list.append(f)
	return audio_list



if __name__ == '__main__':
	path='.'
	audio_list=get_audio_files(get_filepaths(path))
	print(audio_list)
	#print(pa.process_audios(audio_list,3,True))

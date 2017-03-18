"""processAudio.py

Module for processing audio and generating content
based features.

Requires:
		numpy
		scipy
		librosa
		pandas
"""


from multiprocessing import Pool


__version__ = '0.1'
__author__ = 'Subhojeet Pramanik'


import os
import librosa
import numpy as np
import pandas as pd
import scipy
import time


exts=['.mp3','.wav']
show_progress=False


def process_audios(filelist,n_jobs,progress=False):
	'''Generates content based features for 
		a given number of audio file

		Arguments:
			filelist	- 	Tuple containing the list of audio file paths
			n_jobs		-	Number of jobs to run in parallel

		Returns:	pandas.DataFrame

	'''

	#Change global Progress variable
	global show_progress
	show_progress=progress

	# Create the Temp file for keep track of the process count
	with open('/tmp/processAudioProgess.tmp','w') as f:
		f.write('-1\n'+str(len(filelist)))
		f.close()
	
	# Create pool for n jobs ''
	p=Pool(n_jobs)

	# Check list of arguments before processing
	for f in filelist:
		filename, file_extension = os.path.splitext(f)
		if(file_extension not in exts):
			raise ValueError('Invalid arguments specified. Some of the path do not point to a valid audio file.')


	# Process the arguments in parallel
	if(progress):
		display_progress()

	final_df=p.map(generate_audio_features,filelist)

	if(progress):
		print('\t\t------- Completed processing all Audios -------')

	return final_df


def display_progress():
	with open('/tmp/processAudioProgess.tmp','r') as f:
		count=int(f.readline())
		total=int(f.readline())
		count=count+1
		prct=(count/total)*100
		print('\n\t\t------- Completed '+str(round(prct,2))+'% -------\n')
	with open('/tmp/processAudioProgess.tmp','w') as f:
		f.write(str(count)+'\n'+str(total))
		f.close()

def generate_audio_features(path):
	'''Generates content based features for 
		a given Audio file

		Arguments:
			path	-	The location of the Audio file

		Returns:	pandas.DataFrame

	'''

	audio = path
	y,sr=librosa.load(audio)	#Load the audio from the path
	
	## Audio Overview

	if(show_progress):
		print('Audio File: '+path)
		print('Audio Sampling Rate: '+str(sr)+' samples/sec')
		print('Total Samples: '+str(np.size(y)))
		secs=np.size(y)/sr
		print('Audio Length: '+str(secs)+' s')


	###	Seperation of Harmonic and Percussive Signals
	y_harmonic, y_percussive = librosa.effects.hpss(y)


	###	1. Beat Extraction 
	tempo, beat_frames = librosa.beat.beat_track(y=y_harmonic, sr=sr)
	beat_times = librosa.frames_to_time(beat_frames, sr=sr)
	beat_time_diff=np.ediff1d(beat_times)
	beat_nums = np.arange(1, np.size(beat_times))


	###	2. Chroma Energy Normalized (CENS)
	chroma=librosa.feature.chroma_cens(y=y_harmonic, sr=sr)


	###	3. Calculate MFCCs
	mfccs = librosa.feature.mfcc(y=y_harmonic, sr=sr, n_mfcc=13)


	### 4. Spectral Centroid
	cent = librosa.feature.spectral_centroid(y=y, sr=sr)


	### 5. Spectral Contrast
	contrast=librosa.feature.spectral_contrast(y=y_harmonic,sr=sr)


	### 6. Spectral Rolloff
	rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)


	### 7. Zero Crossing Rate
	zrate=librosa.feature.zero_crossing_rate(y_harmonic)


	##	Feature Generation

	###	1. Chroma Energy Normalized
	chroma_mean=np.mean(chroma,axis=1)
	chroma_std=np.std(chroma,axis=1)
	
	chroma_df=pd.DataFrame()	#Empty Dataframe
	for i in range(0,12):
	    chroma_df['chroma_mean_'+str(i)]=chroma_mean[i]
	for i in range(0,12):
	    chroma_df['chroma_std_'+str(i)]=chroma_mean[i]
	chroma_df.loc[0]=np.concatenate((chroma_mean,chroma_std),axis=0)


	###	2. MFCCs
	mfccs_mean=np.mean(mfccs,axis=1)
	mfccs_std=np.std(mfccs,axis=1)

	mfccs_df=pd.DataFrame()	
	for i in range(0,13):
	    mfccs_df['mfccs_mean_'+str(i)]=mfccs_mean[i]
	for i in range(0,13):
	    mfccs_df['mfccs_std_'+str(i)]=mfccs_mean[i]
	mfccs_df.loc[0]=np.concatenate((mfccs_mean,mfccs_std),axis=0)


	### 3. Spectral Features
	cent_mean=np.mean(cent)
	cent_std=np.std(cent)
	cent_skew=scipy.stats.skew(cent,axis=1)[0]


	####Spectral Contrast
	contrast_mean=np.mean(contrast,axis=1)
	contrast_std=np.std(contrast,axis=1)


	#####Spectral Rolloff
	rolloff_mean=np.mean(rolloff)
	rolloff_std=np.std(rolloff)
	rolloff_skew=scipy.stats.skew(rolloff,axis=1)[0]



	###Generate the final Spectral DataFrame
	collist=['cent_mean','cent_std','cent_skew']
	for i in range(0,7):
	    collist.append('contrast_mean_'+str(i))
	for i in range(0,7):
	    collist.append('contrast_std_'+str(i))
	collist=collist+['rolloff_mean','rolloff_std','rolloff_skew']
	
	spectral_df=pd.DataFrame()
	for c in collist:
	    spectral_df[c]=0
	data=np.concatenate(([cent_mean,cent_std,cent_skew],
						contrast_mean,contrast_std,
						[rolloff_mean,rolloff_std,rolloff_std]),
						axis=0)
	spectral_df.loc[0]=data


	### 4. Zero Crossing Rate
	zrate_mean=np.mean(zrate)
	zrate_std=np.std(zrate)
	zrate_skew=scipy.stats.skew(zrate,axis=1)[0]

	zrate_df=pd.DataFrame()
	zrate_df['zrate_mean']=0
	zrate_df['zrate_std']=0
	zrate_df['zrate_skew']=0
	zrate_df.loc[0]=[zrate_mean,zrate_std,zrate_skew]


	### 5. Beat and Tempo
	beat_df=pd.DataFrame()
	beat_df['tempo']=tempo
	beat_df.loc[0]=tempo


	## Generate the Final DataFrame
	final_df=pd.concat((chroma_df,mfccs_df,
						spectral_df,zrate_df,
						beat_df),axis=1)


	## Display the final progress
	if(show_progress):
		display_progress()

	return final_df


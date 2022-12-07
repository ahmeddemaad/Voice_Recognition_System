from Voice_Recognition import app
from flask import request
import os
import numpy as np
from scipy.io import wavfile
import pickle
from sklearn import preprocessing
import librosa
import librosa.display
import python_speech_features as mfcc

def calculate_delta(array):
	
    rows,cols = array.shape
    print(rows)
    print(cols)
    deltas = np.zeros((rows,20))
    N = 2
    for i in range(rows):
        index = []
        j = 1
        while j <= N:
            if i-j < 0:
                first =0
            else:
                first = i-j
            if i+j > rows-1:
                second = rows-1
            else:
                second = i+j 
            index.append((second,first))
            j+=1
        deltas[i] = ( array[index[0][0]]-array[index[0][1]] + (2 * (array[index[1][0]]-array[index[1][1]])) ) / 10
    return deltas


def extract_features(file_path):
    audio , sample_rate = librosa.load(file_path, res_type='kaiser_fast')
    mfcc_feature = mfcc.mfcc(audio,sample_rate, 0.025, 0.01,20,nfft = 1200, appendEnergy = True)    
    mfcc_feature = preprocessing.scale(mfcc_feature)
    print(mfcc_feature)
    delta = calculate_delta(mfcc_feature)
    combined = np.hstack((mfcc_feature,delta)) 
    return combined

def comparing(file_path):
    test = extract_features(file_path)
    call_Ahmed_model=pickle.load(open('Ahmed.gmm','rb'))
    call_mostafa_model=pickle.load(open('mostafa_gmm','rb'))
    call_yahia_model=pickle.load(open('yahia.gmm','rb'))
    scores_1 = np.array(call_Ahmed_model.score(test))
    scores_2 = np.array(call_mostafa_model.score(test))
    scores_3 = np.array(call_yahia_model.score(test))
    return scores_1,scores_2,scores_3


@app.route('/saveRecord',methods =['POST'])
def save_record():
    if request.method =='POST':
        file=request.files['AudioFile']
        file_path='Voice_Recognition/static/assets/recordedAudio.wav'
        file.save(os.path.join(file_path))
        scores_1,scores_2,scores_3=comparing(file_path)
        print(scores_1)
        print(scores_2)
        print(scores_3)
        # if len(audio.shape)>1:
        #     audio=audio[:,0]

from Voice_Recognition import app
from flask import request
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import pickle
from sklearn import preprocessing
import librosa
import librosa.display
import python_speech_features as mfcc
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from matplotlib import cm
from math import log10

def calculate_delta(array):
    rows,cols = array.shape
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
    delta = calculate_delta(mfcc_feature)
    audio_features = np.hstack((mfcc_feature,delta)) 

    # for drawing graphs
    spectral_centroid(audio , sample_rate)
    return audio_features

def loading_models():
    Models=[]
    Models.append(pickle.load(open("./Models/1-ahmedDoor.gmm",'rb')))
    Models.append(pickle.load(open("./Models/3-MustafaDoor.gmm",'rb')))
    Models.append(pickle.load(open("./Models/4-yahiaDoor.gmm",'rb')))
    Models.append(pickle.load(open("./Models/2-aishaDoor.gmm",'rb')))
    return Models


def voice_recognition(audio_features, models):
    listofNames=['ahmed','mostafa','yehia','aisha']
    scores=[]
    for i in range (0 , 4):
        scores.append(models[i].score(audio_features))
    scores.append(0)
    plot(scores)
    scores.pop()
    print(scores)
    Max_index=np.argmax(scores)
    print(Max_index)
    if(Max_index == 0 and np.max(scores ) > -28):
        return listofNames[np.argmax(scores)]
    if(Max_index == 1 and np.max(scores) > -25):
        return listofNames[np.argmax(scores)]  
    if(Max_index == 2 and np.max(scores) > -29):
        return listofNames[np.argmax(scores)]
    if(Max_index == 3 and np.max(scores) > -25):
        return listofNames[np.argmax(scores)]  
    else:
        return "others"



def plot(scores):
    labels = ["Ahmed","Moustafa","Yehia","Aisha",""]

    thresholds = [72, 75, 71, 75, 0]

    
    for i in range (0,4) :
        scores[i] += 100

    #number of data points
    n = len(thresholds)

    #radius of donut chart
    r = 1.5
    #calculate width of each ring
    w = r / n 

    #create colors along a chosen colormap
    colors = [cm.terrain(i / n) for i in range(n)]

    #create figure, axis
    fig, ax = plt.subplots()
    ax.axis("equal")

    #create rings of donut chart
    for i in range(n):
    #hide labels in segments with textprops: alpha = 0 - transparent, alpha = 1 - visible
        innerring, _ = ax.pie([100 - thresholds[i], thresholds[i]], radius = r - i * w, startangle = 90, labels = ["", labels[i]], labeldistance = 1 - 1 / (1.5 * (n - i)), textprops = {"alpha": 0}, colors = ["black", colors[i]])
        plt.setp(innerring, width = w, edgecolor = "white")

        innerring, _ = ax.pie([100 - scores[i], scores[i]], radius = r - i * w, startangle = 90, labeldistance = 1 - 1 / (1.5 * (n - i)), textprops = {"alpha": 0}, colors = ["white", colors[i]])
        plt.setp(innerring, width = w, edgecolor = "white", alpha=0.7)

    plt.legend()
    name = 'radar'
    image_file_name='Voice_Recognition/static/assets/'+str(name)+'.jpg'
    plt.savefig(image_file_name)

    for i in range (0,4) :
        scores[i] -= 100
    return

# graphs

def spectral_centroid(y, sr):
    cent = librosa.feature.spectral_centroid(y=y, sr=sr)
    S, phase = librosa.magphase(librosa.stft(y=y))
    librosa.feature.spectral_centroid(S=S)
    freqs, times, D = librosa.reassigned_spectrogram(y, fill_nan=True)
    librosa.feature.spectral_centroid(S=np.abs(D), freq=freqs)
    times = librosa.times_like(cent)
    fig, ax = plt.subplots()
    librosa.display.specshow(librosa.amplitude_to_db(S, ref=np.max),y_axis='log', x_axis='time', ax=ax)
    ax.plot(times, cent.T, label='Spectral centroid', color='w')
    ax.legend(loc='upper right')
    ax.set(title='log Power spectrogram')
    name = 'spectral_centroid'
    image_file_name='Voice_Recognition/static/assets/'+str(name)+'.jpg'
    plt.savefig(image_file_name)
    return


models = []
models.clear()
models=loading_models()

@app.route('/saveRecord',methods =['POST'])
def save_record():
    if request.method =='POST':
        file=request.files['AudioFile']
        file_path='Voice_Recognition/static/assets/recordedAudio.wav'
        file.save(os.path.join(file_path))

        audio_features = extract_features(file_path)
        name = voice_recognition(audio_features, models)
        return(name)


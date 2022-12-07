import librosa
from matplotlib import pyplot as plt
import numpy as np
import librosa.display

def spectrogram(y):
    MO = librosa.stft(y)  # Short-Time Fourier Transform of y
    s_db = librosa.amplitude_to_db(np.abs(MO), ref=np.max) # convert amplitude to decibel. In other words, it get the complex number (a +bj) and get its magnitude 
    fig, ax = plt.subplots() 
    img = librosa.display.specshow(s_db, x_axis='time', y_axis='linear', ax=ax) # getting the spectrogram
    fig.colorbar(img, ax=ax, format="%+2.f dB")
    fig.savefig('spectrogram.png') # saving the spectrogram as png (image)
    return MO

y, sr = librosa.load("Voice_Recognition/static/assets/recordedAudio.wav") # accessing the file

a = spectrogram(y)
print(a)
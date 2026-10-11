import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt

audio, sr = librosa.load("sai_vardhan_asr_test.wav", sr=16000)

D = librosa.stft(audio)
db = librosa.amplitude_to_db(abs(D), ref=np.max)

plt.figure(figsize=(12, 5))
librosa.display.specshow(
    db,
    sr=sr,
    x_axis="time",
    y_axis="hz"
)

plt.colorbar(format="%+2.0f dB")
plt.title("Audio Spectrogram")
plt.show()
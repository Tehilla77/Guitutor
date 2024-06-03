from scipy.io import wavfile
from scipy.signal import butter, lfilter
import numpy as np
from more_functions import convert_to_wav


# Define a butterworth high-pass filter
def butter_highpass(cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a


def highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y


# Load audio file
path = convert_to_wav(r"C:\Users\t0527\OneDrive\שולחן העבודה\פרויקט סופי בינה\server_side\songs\baavur-avoteinoo.mp3",
                      '.')
fs, data = wavfile.read(path)

# Apply high-pass filter
filtered_data = highpass_filter(data, 300, fs)

# Save filtered audio
wavfile.write('filtered_audio.wav', fs, filtered_data.astype(np.int16))

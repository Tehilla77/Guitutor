import joblib
import pandas as pd
from build_chord_classifcation_model_rfc import find_harmonics
from pydub import AudioSegment
import os

model = joblib.load('rfc_model.pkl')


def save_song_data(filename):
    data = []
    max_harm_length = 0
    freq_peaks = find_harmonics(filename)
    max_harm_length = max(max_harm_length, len(freq_peaks))
    cur_data = [filename]
    cur_data.extend([freq_peaks.min(), freq_peaks.max(), len(freq_peaks)])
    cur_data.extend(freq_peaks)
    data.append(cur_data)

    # Create columns for DataFrame
    cols = ["File Name", "Min Harmonic", "Max Harmonic", "# of Harmonics"]
    for i in range(max_harm_length):
        cols.append("Harmonic {}".format(i + 1))

    print(f"Length of cur_data: {len(cur_data)}")
    print(f"Number of columns: {len(cols)}")

    # Ensure the number of columns matches the data length
    if len(cur_data) != len(cols):
        raise ValueError("Number of columns does not match the data length")

    # Creating DataFrame
    df = pd.DataFrame(data, columns=cols)

    for i in range(1, 21):
        curr_interval = "Interval {}".format(i)
        curr_harm = "Harmonic {}".format(i + 1)
        prev_harm = "Harmonic {}".format(i)
        if curr_harm in df.columns and prev_harm in df.columns:
            df[curr_interval] = df[curr_harm].div(df[prev_harm], axis=0)

    for i in range(2, 14):
        curr_interval = "Interval {}_1".format(i)
        curr_harm = "Harmonic {}".format(i)
        if curr_harm in df.columns:
            df[curr_interval] = df[curr_harm].div(df["Harmonic 1"], axis=0)

    columns = ["Interval 1", "Interval 2", "Interval 3", "Interval 4"]
    columns.extend(["Interval 4_1", "Interval 5_1", "Interval 6_1"])
    return df[columns]


def convert_to_wav(mp3_file, output_dir):
    audio = AudioSegment.from_mp3(mp3_file)
    wav_file = os.path.join(output_dir, os.path.splitext(os.path.basename(mp3_file))[0] + ".wav")
    audio.export(wav_file, format="wav")
    return wav_file


def get_prediction(audio_file):
    # Convert MP3 to WAV
    file_name, file_extension = os.path.splitext(audio_file)

    # Convert to WAV if the file is MP3
    if file_extension.lower() == ".mp3":
        wav_file = convert_to_wav(audio_file, output_dir=".")
    else:
        wav_file = audio_file

    # Process WAV file
    file_data = save_song_data(wav_file)
    print(file_data)
    prediction = model.predict(file_data.iloc[[0]])
    if prediction == 0:
        return "Minor"
    return "Major"


# Test the function with debugging
get_prediction(r"C:\Users\User\Desktop\פרויקט בינה מלאכותית 20.5.24\Audio_Files\Major\Major_2.wav")

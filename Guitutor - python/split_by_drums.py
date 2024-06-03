import os

import librosa
import numpy as np
from pydub import AudioSegment
import scipy.io.wavfile as wavfile
from recognize_chord_name import find_chord

# Load the audio file
drums_path = r"C:\Users\User\Desktop\פרויקט סופי בינה\server_side\seperate to vocal drums instroumental and bass\seperate songs\porchim_drums.mp3"
other_path = r"C:\Users\User\Desktop\פרויקט סופי בינה\server_side\seperate to vocal drums instroumental and bass\seperate songs\porchim_other.mp3"

# Function to separate stems (implement or use your existing function)
# def separate_stems(other_path):
#     y, sr = librosa.load(other_path, sr=None)
#     return y, sr


# Separate the stems
drums_stem, sr = librosa.load(drums_path)

# Detect drum beats
tempo, beats = librosa.beat.beat_track(y=drums_stem, sr=sr)
beat_times = librosa.frames_to_time(beats, sr=sr)
print("Detected beats at times (seconds):", beat_times)

# Load the audio file into a pydub AudioSegment for easy slicing
audio_segment = AudioSegment.from_file(other_path)


# Function to convert librosa time to pydub milliseconds
def time_to_ms(time):
    return int(time * 1000)


# Create segments based on beat times and return as numpy arrays
def create_segments(audio_segment, beat_times):
    segments = []
    for i in range(len(beat_times) - 1):
        start_time = time_to_ms(beat_times[i])
        end_time = time_to_ms(beat_times[i + 1])
        segment = audio_segment[start_time:end_time]
        segment_array = np.array(segment.get_array_of_samples()).reshape(-1, audio_segment.channels)
        segments.append(segment_array)

    # Handle the last segment (from the last beat to the end of the audio)
    if beat_times[-1] < len(audio_segment) / 1000.0:
        start_time = time_to_ms(beat_times[-1])
        segment = audio_segment[start_time:]
        segment_array = np.array(segment.get_array_of_samples()).reshape(-1, audio_segment.channels)
        segments.append(segment_array)

    return segments


segments = create_segments(audio_segment, beat_times)


# Function to recognize chord from a segment (dummy implementation)
# def recognize_chord(segment):
#     # Dummy implementation: replace with your actual chord recognition code
#     return "Chord"


# Recognize chords for each segment
def build_arr_chords():
    recognized_chords = []
    for index, segment in enumerate(segments):
        if index > 5:
            seg_path = save_segment_to_wav(segment, sr, index)
            chord = find_chord(seg_path)
            print(chord)
            recognized_chords.append(chord)
            print(f"Recognized chord: {chord}")
            print(recognized_chords)
    return recognized_chords


def save_segment_to_wav(segment, sr, i):
    s_path = rf'{os.getcwd()}\songs\segment_section\{i}.wav'
    wavfile.write(s_path, sr, segment)
    return s_path


# Example usage:
# segment = segments[0]  # Using the first segment for example
# save_segment_to_wav(segment, sr, "output_segment.wav")

# Example: returning segments and recognized chords
def process_audio(other_path):
    y, sr = librosa.load(other_path, sr=None)
    drum_stem = drums_stem
    tempo, beats = librosa.beat.beat_track(y=drum_stem, sr=sr)
    beat_times = librosa.frames_to_time(beats, sr=sr)
    audio_segment = AudioSegment.from_file(other_path)
    segments = create_segments(audio_segment, beat_times)

    # recognized_chords = []
    # for segment in segments:
    #     chord = recognize_chord(segment)
    #     recognized_chords.append(chord)
    recognized_chords = build_arr_chords()

    return segments, recognized_chords


# Example usage
segments, chords = process_audio(other_path)
print("Segments and chords processed.")

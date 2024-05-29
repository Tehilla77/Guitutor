import os
from mutagen.mp3 import MP3
from pydub import AudioSegment


def get_mp3_duration(file_path):
    audio = MP3(file_path)
    duration_in_seconds = audio.info.length
    return duration_in_seconds


def cut_song(file_path, name):
    song = AudioSegment.from_mp3(file_path)
    duration = int(get_mp3_duration(file_path))
    dir_path = rf'{os.getcwd()}\songs\{name}\section'
    os.makedirs(dir_path)
    print(f"Duration: {duration} seconds")
    second = 1000
    for i in range(duration):
        last = i - 1
        current_song = song[last * second:i * second]
        current_song.export(rf"{dir_path}\sep_{i}.wav", format="wav")

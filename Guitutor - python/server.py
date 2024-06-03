from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
from pydub import AudioSegment

# import our python files: #
import split_to_sources
from cut_song_to_sections import cut_song
from more_functions import makedir
# from recognize_chord_name import get_chords_of_song

os.environ["FFPROBE_PATH"] = r"C:\ffmpeg\bin\ffprobe.exe"

app = Flask(__name__)


@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist('song_file')
        print(files)
        if files:
            file = files[0]
            audio_data = file.read()
            fname = file.filename.split(".")
            global name
            name = fname[0]
            format_file = fname[1]
            # save the audio file # 
            with tempfile.NamedTemporaryFile(delete=False, suffix=format_file) as tmp_file:
                tmp_file.write(audio_data)
                tmp_filename = tmp_file.name

            print("accept and save file :" + name + " " + format_file)

            audio = AudioSegment.from_file(tmp_filename)

            # create folders according to song name to save all the song files #
            router_song_dir = rf"{os.getcwd()}\songs"
            output_folder = rf"{router_song_dir}\{name}"
            makedir(router_song_dir)
            makedir(output_folder)
            # save song in matching folder #
            audio.export(rf"{output_folder}\{name}.{format_file}", format="mp3")
            os.unlink(tmp_filename)
            print("Delete the temporary file")

            song_path = rf"{output_folder}\{name}.{format_file}"

            # check if we need to erase it!!! #

            split_to_sources.load_song(song_path)
            split_to_sources.build_vocal_drums(name)
            split_to_sources.build_playback(name)
            split_to_sources.build_song_without_guitar(name)

            path_other = split_to_sources.build_other(name)

            # Use lala.ai to get the Acoustic guitar tune from the song and save it instead of path_other var #

            # Function that cut the song to seconds (according the drums?!) #
            section_path = cut_song(path_other, name)
            # get_chords_of_song(section_path)

            os.remove(song_path)

            return jsonify({f'Audio file saved as {output_folder}': 'ok'})
        return jsonify({'No file uploaded': 'not-ok'})


@app.route('/upload_record', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return "No file part", 400

    file = request.files['audio']
    if file.filename == '':
        return "No selected file", 400
    dir = rf'{os.getcwd()}\songs'
    # Save the webm file
    webm_path = os.path.join(dir, 'user_recording.webm')
    file.save(webm_path)

    # Convert to wav
    wav_path = os.path.join(dir, 'user_recording.wav')
    audio = AudioSegment.from_file(webm_path, format='webm')
    audio.export(wav_path, format='wav')
    # Optionally, convert to mp3
    mp3_path = os.path.join(dir, 'user_recording.mp3')
    audio.export(mp3_path, format='mp3')
    os.remove(webm_path)
    os.remove(wav_path)
    split_to_sources.load_song(mp3_path)
    split_to_sources.build_drums(name)
    split_to_sources.build_other(name)


@app.route('/get_vocal', methods=['GET'])
def return_vocal_drums():
    try:
        return send_file(rf"{os.getcwd()}\songs\{name}\{name}_vocal_drums.mp3")
    except Exception as e:
        return str(e)


@app.route('/get_playback', methods=['GET'])
def return_playback():
    try:
        return send_file(rf"{os.getcwd()}\songs\{name}\{name}_playback.mp3")
    except Exception as e:
        return str(e)


@app.route('/get_song_without_guitar', methods=['GET'])
def return_song_without_guitar():
    try:
        return send_file(rf"{os.getcwd()}\songs\{name}\{name}_song_without_guitar.mp3")
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    CORS(app)
    app.run()

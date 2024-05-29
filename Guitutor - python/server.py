from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import io
from pydub import AudioSegment

# import our python files: #
import split_to_sources
from cut_song_to_sections import cut_song
from more_functions import makedir

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

            global output_folder
            router_song_dir = rf"{os.getcwd()}\songs"
            output_folder = rf"{router_song_dir}\{name}"
            makedir(router_song_dir)
            makedir(output_folder)

            audio.export(rf"{output_folder}\{name}.{format_file}", format="mp3")
            song_path = rf"{output_folder}\{name}.{format_file}"
            os.unlink(tmp_filename)
            print("Delete the temporary file")

            # check if we need to erase it!!! #

            split_to_sources.load_song(song_path)
            split_to_sources.build_vocal_drums(name)
            split_to_sources.build_playback(name)
            split_to_sources.build_song_without_guitar(name)
            path_other = split_to_sources.build_other(name)

            # Use lala.ai to get the Acoustic guitar tune from the song #

            cut_song(path_other, name)
            os.remove(song_path)

            # Function that cut the song to seconds (according the drums?!) #

            return jsonify({f'Audio file saved as {output_folder}': 'ok'})
        return jsonify({'No file uploaded': 'not-ok'})


@app.route('/get_vocal_drums', methods=['GET'])
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

from flask import Flask, request, render_template, send_from_directory
import sys
import sounddevice as sd
import wavfile
sys.path.append('../')

from modeltest.file_processing import stt, tts
from image_generation.text_to_image import generate_image
import os

app = Flask(__name__)

folder_path = os.path.join(os.path.dirname(__file__), 'files')

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    audio_file = request.files['audio']
    # Obtén el valor del campo 'language' del formulario
    lang = request.form['lang']
    # Obtén el nombre original del archivo
    filename = audio_file.filename
    # make sure that the folder exists
    os.makedirs(folder_path, exist_ok=True)

    # Combina la ruta de la carpeta "files" con el nombre de archivo
    save_path = os.path.join(folder_path, filename)
    # Guarda el archivo en la ruta especificada
    audio_file.save(save_path)

    result = stt(save_path, lang)

    tts(text_to_convert = result, lang=lang, save_path=save_path)

    audio_path = "/public/" + filename

    return render_template('result.html', result=result,lang=lang,audio_path=audio_path)

recording = None  # Global variable to store the recording

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    global recording

    fs = 44100  # Sample rate
    output_file = "output.wav"  # Output file name

    print("Recording started...")

    # Start recording audio in a continuous loop
    recording = sd.rec(int(fs * 10), samplerate=fs, channels=2)

    return "Recording started"

@app.route('/stop', methods=['POST'])
def stop():
    global recording

    if recording is None:
        return "No recording in progress"

    print("Recording stopped.")

    # Stop recording
    sd.stop()
    fs = 44100  # Sample rate
    save_path = os.path.join(folder_path, "recording.wav")
    # Save the recorded audio as a WAV file
    wavfile.write(save_path, fs, recording)
    
    print("Audio saved as", save_path)

    recording = None  # Reset the recording variable

    return "Recording stopped. Audio saved as " + output_file

# I wanna do a text to image function
@app.route('/text-to-image', methods=['POST'])
def text_to_image():
    # tHE ATTRIBUs will be prompt steps weight and seed
    prompt = request.form['prompt']
    steps = int(request.form['steps'])
    weight = int(request.form['weight'])
    seed = int(request.form['seed'])

    return generate_image(prompt, steps, weight, seed)


@app.route('/public/<path:filename>')
def serve_file(filename):
    return send_from_directory(folder_path, filename)


if __name__ == '__main__':
    app.run()

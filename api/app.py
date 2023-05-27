from flask import Flask, request
# import transcribe as transcribe from a directory that is ../modeltest
import sys
sys.path.append('../')

from modeltest.file_processing import stt, tts
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return '¡Hola, Flask!'

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    audio_file = request.files['audio']
    # Obtén el nombre original del archivo
    filename = audio_file.filename
    # Obtén la ruta absoluta de la carpeta "files"
    
    folder_path = os.path.join(os.path.dirname(__file__), 'files')
    # make sure that the folder exists
    os.makedirs(folder_path, exist_ok=True)

    # Combina la ruta de la carpeta "files" con el nombre de archivo
    save_path = os.path.join(folder_path, filename)
    # Guarda el archivo en la ruta especificada
    audio_file.save(save_path)
    result = stt(save_path)

    tts(text_to_convert = result, save_path=save_path)


    return result #'Archivo de audio y texto recibido correctamente'

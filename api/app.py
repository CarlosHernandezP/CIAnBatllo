from flask import Flask, request
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
    # Combina la ruta de la carpeta "files" con el nombre de archivo
    save_path = os.path.join(folder_path, filename)
    # Guarda el archivo en la ruta especificada
    audio_file.save(save_path)



    return 'Archivo de audio recibido correctamente'

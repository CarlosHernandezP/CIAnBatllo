from flask import render_template, Response, request
from controllers.audio_controller import upload_audio, audio
from flask import Blueprint

# Crear un Blueprint llamado 'audio_routes'
audio_routes = Blueprint('audio_routes', __name__)

@audio_routes.route('/audio')
def audio_route():
    """
    Ruta para mostrar la página de audio.
    Llama a la función 'audio' del controlador.
    """
    return audio()

@audio_routes.route('/upload-audio', methods=['POST'])
def upload_audio_route():
    """
    Ruta para manejar la carga de archivos de audio.
    Llama a la función 'upload_audio' del controlador.
    """
    # Obtener el archivo de audio y el idioma desde la solicitud
    audio_file = request.files['audio']
    lang = request.form['lang']

    # Llamar a la función de controlador para manejar la carga de audio
    return upload_audio(audio_file, lang)

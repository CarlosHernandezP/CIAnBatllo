# main_controller.py
from flask import render_template, Response, send_from_directory
import sys
import os
sys.path.append('../')
from modeltest.file_processing import stt, tts
from image_generation.text_to_image import generate_image

# Obtén la ruta del directorio actual del script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Combina la ruta del directorio padre con la carpeta "files"
folder_path = os.path.join(current_dir, '..', 'static')

def index():
    return render_template('index.html')

def upload_audio(audio_file, lang):
    # Obtén el nombre original del archivo
    filename = audio_file.filename
    # Combina la ruta de la carpeta "audios" con el nombre de archivo
    save_path = os.path.join(folder_path, 'audios', filename)
    # Asegúrate de que la carpeta "audios" exista
    os.makedirs(os.path.join(folder_path, 'audios'), exist_ok=True)
    # Guarda el archivo en la ruta especificada
    audio_file.save(save_path)

    result = stt(save_path, lang)

    tts(text_to_convert=result, lang=lang, save_path=save_path)

    audio_path = "/public/audios/" + filename

    return render_template('audio_view.html', result=result, lang=lang, audio_path=audio_path)


def text_to_image(prompt, steps, weight, seed):
    image_path = generate_image(prompt, steps, weight, seed)
    return render_template('image_view.html', image_path=image_path)


def move_to_folder(filename):
    return send_from_directory(folder_path, filename)



def audio():
    return render_template('audio.html')

def image():
    return render_template('image.html')
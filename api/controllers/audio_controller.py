from flask import render_template, Response
import os
import whisper
from mtranslate import translate
from gtts import gTTS

# Obtén la ruta del directorio del script actual
current_dir = os.path.dirname(os.path.abspath(__file__))
# Combina la ruta del directorio padre con la carpeta "files"
folder_path = os.path.join(current_dir, '..', 'static', 'audios')

def audio():
    """
    Ruta para mostrar la página de audio.
    """
    return render_template('audio.html')

def upload_audio(audio_file, lang):
    """
    Ruta para manejar la carga de archivos de audio.
    """
    # Combina la ruta de la carpeta "audios" con el nombre de archivo
    save_path = os.path.join(folder_path, audio_file.filename)
    # Asegúrate de que la carpeta "audios" exista
    os.makedirs(folder_path, exist_ok=True)
    # Guarda el archivo en la ruta especificada
    audio_file.save(save_path)

    # Realiza el reconocimiento de voz y sintetización de texto a voz
    result = stt(save_path, lang)
    tts(text_to_convert=result, lang=lang, save_path=save_path)

    # Ruta para acceder al archivo de audio en la página
    audio_path = "/public/audios/" + audio_file.filename

    # Renderiza la página de visualización de audio con los resultados
    return render_template('audio_view.html', result=result, lang=lang, audio_path=audio_path)

def stt(audio_path: str, lang: str = 'it') -> str:
    """
    Convierte discurso a texto.

    Parameters
    ----------
    audio_path : str
        Ruta del archivo de audio a convertir.

    Returns
    -------
    str
        Texto convertido del discurso.
    """
    # Carga el modelo de reconocimiento de voz
    model = whisper.load_model('base')
    # Transcribe el audio utilizando el modelo
    result = model.transcribe(audio_path)

    # Extrae el texto transcrito y lo convierte a minúsculas
    input_string = result.get("text", "").lower()

    # Traduce el texto al idioma objetivo
    translated_text = translate_text(text_to_translate=input_string, lang=lang)

    return translated_text


def tts(text_to_convert: str = None, save_path: str = None, lang: str = 'it') -> None:
    """
    Convierte texto a habla y lo guarda en un archivo.

    Parameters
    ----------
    text_to_convert : str
        Texto para convertir a habla.
    save_path : str
        Ruta donde guardar el archivo de audio.
    lang : str
        Idioma del texto a convertir.

    Returns
    -------
    None
    """
    # Crea un objeto de texto a voz con el texto y el idioma especificados
    tts = gTTS(text=text_to_convert, lang=lang)

    # Guarda el resultado del texto a voz en un archivo de audio
    tts.save(save_path)

    return


def translate_text(text_to_translate: str, lang: str = 'en') -> str:
    """
    Traduce texto a otro idioma.

    Parameters
    ----------
    text_to_translate : str
        Texto para traducir.
    lang : str
        Idioma del texto a traducir.

    Returns
    -------
    str
        Texto traducido.
    """
    # Utiliza la función de traducción para obtener el texto traducido
    translated_text = translate(text_to_translate, lang)

    return translated_text

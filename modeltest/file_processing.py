import whisper
from mtranslate import translate
from gtts import gTTS


def stt(audio_path : str, lang : str='it') -> str:
    """
    Convert speech to text

    Parameters
    ----------
    audio_path : str path of the audio file to convert

    Returns
    -------
    str : text converted from speech
    """

    model = whisper.load_model('base')
    result = model.transcribe(audio_path)


    input_string = result["text"].lower()
    # Translate text to the target language
    translated_text = translate_text(text_to_translate = input_string,
                                lang = lang)

    return translated_text

def tts(text_to_convert : str=None, save_path : str=None, lang : str='it') ->None:
    """
    Convert text to speech and save it to a file

    Parameters
    ----------
    text_to_convert : str text to convert to speech
    save_path : str       path where to save the audio file
    lang : str :         language of the text to convert

    Returns
    -------
    None
    """


    tts = gTTS(text=text_to_convert, lang=lang)

    tts.save(save_path)  # Save the TTS result to an audio file

    return 

def translate_text(text_to_translate : str, lang : str='en') -> str:
    """
    Translate text to another language

    Parameters
    ----------
    text_to_translate : str text to translate
    lang : str :         language of the text to translate

    Returns
    -------
    str : translated text
    """

    translated_text = translate(text_to_translate, lang)

    return translated_text


if __name__ == '__main__':
    path = '../api/files/CHROMATICS .mp3'
    text_from_audio = stt(path)
    translated_text = translate_text(text_from_audio)

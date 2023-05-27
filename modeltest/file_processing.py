import whisper
from gtts import gTTS


def stt(audio_path : str) -> str:
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

    return input_string

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

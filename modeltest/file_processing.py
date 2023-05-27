import whisper
from gtts import gTTS


def stt(audio_path : str) -> str:
    model = whisper.load_model('base')
    result = model.transcribe(audio_path)


    input_string = result["text"].lower()

    return input_string

def tts(text_to_convert : str=None, save_path : str=None, lang : str='it') ->None:
    tts = gTTS(text=text_to_convert, lang=lang)

    tts.save(save_path)  # Save the TTS result to an audio file

    return 
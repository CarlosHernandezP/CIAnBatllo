import whisper
import ggts import gTTS


def stt(audio_path : str) -> str:
    model = whisper.load_model('base')
    result = model.transcribe(audio_path)


    input_string = result["text"].lower()

    return input_string

def tts(text_to_convert : str=None) ->:

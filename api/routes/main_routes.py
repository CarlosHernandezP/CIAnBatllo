# main_routes.py
from flask import render_template, Response, request
from controllers.main_controller import index, upload_audio, text_to_image, video_feed, move_to_folder,video, audio, image
from flask import Blueprint

main_routes = Blueprint('main_routes', __name__)

@main_routes.route('/')
def index_route():
    return index()

@main_routes.route('/upload-audio', methods=['POST'])
def upload_audio_route():
    audio_file = request.files['audio']
    lang = request.form['lang']
    return upload_audio(audio_file, lang)

@main_routes.route('/text-to-image', methods=['POST'])
def text_to_image_route():
    prompt = request.form['prompt']
    steps = int(request.form['steps'])
    weight = int(request.form['weight'])
    seed = int(request.form['seed'])
    return text_to_image(prompt,steps,weight,seed)

@main_routes.route('/public/<path:filename>')
def serve_file(filename):
    return move_to_folder(filename)

@main_routes.route('/video')
def video_route():
    return video()

@main_routes.route('/video_feed')
def video_feed_route():
    return video_feed()

@main_routes.route('/audio')
def audio_route():
    return audio()

@main_routes.route('/image')
def image_route():
    return image()
from flask import render_template, Response, request
from controllers.video_controller import video_feed, video
from flask import Blueprint

# Crear un Blueprint llamado 'video_routes'
video_routes = Blueprint('video_routes', __name__)

@video_routes.route('/video')
def video_route():
    """
    Ruta para mostrar la página de video.
    Llama a la función 'video' del controlador.
    """
    return video()

@video_routes.route('/video_feed')
def video_feed_route():
    """
    Ruta para transmitir el video en tiempo real.
    Llama a la función 'video_feed' del controlador.
    """
    return video_feed()


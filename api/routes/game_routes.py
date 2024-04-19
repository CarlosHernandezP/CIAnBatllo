from flask import render_template, Response, request
from controllers.game_controller import game,video_game
from flask import Blueprint

# Crear un Blueprint llamado 'audio_routes'
game_routes = Blueprint('game_routes', __name__)

# Ruta para la página principal
@game_routes.route('/game')
def index_game():
    # Llama a la función index del controlador principal
    return game()

@game_routes.route('/video_game')
def video_screen_game():
    """
    Ruta para transmitir el video en tiempo real.
    Llama a la función 'video_feed' del controlador.
    """
    return video_game()
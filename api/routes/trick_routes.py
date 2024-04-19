from flask import render_template, Response, request
from controllers.trick_controller import trick
from flask import Blueprint

# Crear un Blueprint llamado 'audio_routes'
trick_routes = Blueprint('trick_routes', __name__)

# Ruta para la página principal
@trick_routes.route('/trick')
def index_trick():
    # Llama a la función index del controlador principal
    return trick()

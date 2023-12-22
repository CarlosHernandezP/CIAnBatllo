# main_routes.py
from flask import render_template, Response, request
from controllers.main_controller import index
from flask import Blueprint

# Crea un Blueprint para las rutas principales
main_routes = Blueprint('main_routes', __name__)

# Ruta para la página principal
@main_routes.route('/')
def index_route():
    # Llama a la función index del controlador principal
    return index()

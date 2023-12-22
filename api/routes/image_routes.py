# main_routes.py
from flask import render_template, Response, request
from controllers.image_controller import text_to_image, move_to_folder, image
from flask import Blueprint

# Crea un Blueprint para las rutas relacionadas con imágenes
image_routes = Blueprint('image_routes', __name__)

# Ruta para mostrar la página de imágenes
@image_routes.route('/image')
def image_route():
    return image()

# Ruta para manejar la solicitud de generación de imágenes a partir de texto
@image_routes.route('/text-to-image', methods=['POST'])
def text_to_image_route():
    # Obtén los datos del formulario enviado
    prompt = request.form['prompt']
    steps = int(request.form['steps'])
    weight = int(request.form['weight'])
    seed = int(request.form['seed'])

    # Llama a la función text_to_image con los parámetros proporcionados
    return text_to_image(prompt, steps, weight, seed)

# Ruta para servir archivos estáticos desde el directorio "public"
@image_routes.route('/public/<path:filename>')
def serve_file(filename):
    # Llama a la función move_to_folder para servir el archivo solicitado
    return move_to_folder(filename)



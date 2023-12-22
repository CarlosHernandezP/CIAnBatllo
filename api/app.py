from flask import Flask
from routes.main_routes import main_routes
from routes.video_routes import video_routes
from routes.audio_routes import audio_routes
from routes.image_routes import image_routes

# Crear una instancia de la aplicación Flask
app = Flask(__name__)

# Registrar los blueprints en la aplicación
app.register_blueprint(main_routes)
app.register_blueprint(video_routes)
app.register_blueprint(audio_routes)
app.register_blueprint(image_routes)

if __name__ == '__main__':
    """
    Si el script es ejecutado directamente, iniciar el servidor de desarrollo.
    """
    app.run()

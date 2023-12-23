from flask import Flask
from flask_socketio import SocketIO  # Asegúrate de importar SocketIO
from routes.main_routes import main_routes
from routes.video_routes import video_routes
from routes.audio_routes import audio_routes
from routes.image_routes import image_routes
from routes.game_routes import game_routes
from controllers.game_controller import init_socketio  # Asegúrate de que la importación sea correcta

# Crear una instancia de la aplicación Flask
app = Flask(__name__)
socketio = SocketIO(app)

# Inicializar SocketIO con la aplicación Flask
init_socketio(app)

# Registrar los blueprints en la aplicación
app.register_blueprint(main_routes)
app.register_blueprint(video_routes)
app.register_blueprint(audio_routes)
app.register_blueprint(image_routes)
app.register_blueprint(game_routes)

if __name__ == '__main__':
    """
    Si el script es ejecutado directamente, iniciar el servidor de desarrollo.
    """
    socketio.run(app, debug=True)
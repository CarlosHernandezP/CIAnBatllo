# api/app.py
from flask import Flask
from routes.main_routes import main_routes
from routes.video_routes import video_routes

app = Flask(__name__)
app.register_blueprint(main_routes)
app.register_blueprint(video_routes)

if __name__ == '__main__':
    app.run()
